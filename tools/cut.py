import onnxruntime as ort,numpy as np,time
from PIL import Image,ImageFilter
from scipy import ndimage
Image.MAX_IMAGE_PIXELS=None
_s=None
def sess():
    global _s
    if _s is None:
        o=ort.SessionOptions(); o.intra_op_num_threads=4
        _s=ort.InferenceSession('birefnet.onnx',o,providers=['CPUExecutionProvider'])
    return _s
M=np.array([0.485,0.456,0.406],np.float32);S=np.array([0.229,0.224,0.225],np.float32)
def matte(im):
    x=(np.array(im.convert('RGB').resize((1024,1024),Image.BICUBIC)).astype(np.float32)/255-M)/S
    y=sess().run(None,{'input_image':x.transpose(2,0,1)[None]})[0][0,0]
    p=1/(1+np.exp(-y))
    m=Image.fromarray((p*255).astype(np.uint8)).resize(im.size,Image.BICUBIC)
    a=np.array(m)
    lab,n=ndimage.label(a>128)
    if n>1:
        sz=ndimage.sum(np.ones_like(a),lab,range(1,n+1)); keep=lab==(np.argmax(sz)+1)
        keep=ndimage.binary_dilation(keep,iterations=max(4,im.size[0]//250))
        a=np.where(keep,a,0)
    # fill holes (windows etc are part of car)
    solid=ndimage.binary_fill_holes(a>128); a=np.where(solid&(a<=128),255,a)
    return a.astype(np.uint8)
def defringe(rgb,a):
    # pull edge colours from the car interior to avoid background halos
    arr=np.array(rgb).astype(np.float32); inner=(a>250)
    w=ndimage.gaussian_filter(inner.astype(np.float32),3)+1e-6
    blur=np.stack([ndimage.gaussian_filter(arr[...,c]*inner,3) for c in range(3)],-1)/w[...,None]
    edge=(a>0)&(a<250); t=(1-a/255.0)[...,None]
    arr[edge]=(arr*(1-t)+blur*t)[edge]
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
