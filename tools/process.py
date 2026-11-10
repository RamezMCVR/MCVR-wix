import json,os,sys,urllib.request,urllib.parse,time,numpy as np
sys.path.insert(0,'tools'); from cut import matte,defringe,Image
UA={'User-Agent':'MCVR-photo-fetch/1.0 (github.com/RamezMCVR/MCVR-wix)'}
P=json.load(open('tools/picks.json')); os.makedirs('work/cut',exist_ok=True)
OW,OH=1800,1200
for k,x in P.items():
    if os.path.exists(f'work/cut/{k}.png'): continue
    u='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(x['title'].replace(' ','_'))
    for i in range(4):
        try: b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read(); break
        except Exception as e: print('retry',k,e); time.sleep(5)
    open('/tmp/o.jpg','wb').write(b)
    im=Image.open('/tmp/o.jpg'); 
    from PIL import ImageOps; im=ImageOps.exif_transpose(im).convert('RGB')
    im.thumbnail((4000,4000),Image.LANCZOS)
    a=matte(im); rgb=defringe(im,a)
    ys,xs=np.where(a>40); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max(); cw,ch=x1-x0,y1-y0
    bw=max(cw*1.10,ch*1.22*1.5); bh=bw/1.5; cx,cy=(x0+x1)/2,(y0+y1)/2
    car=rgb.convert('RGBA'); car.putalpha(Image.fromarray(a))
    canvas=Image.new('RGBA',(int(bw),int(bh)),(0,0,0,0)); canvas.paste(car,(int(bw/2-cx),int(bh/2-cy)),car)
    canvas.resize((OW,OH),Image.LANCZOS).save(f'work/cut/{k}.png',optimize=True)
    print(k,im.size,flush=True)
