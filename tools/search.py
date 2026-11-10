import json,urllib.request,urllib.parse,os,time
UA={'User-Agent':'MCVR-photo-fetch/1.0 (github.com/RamezMCVR/MCVR-wix)'}
def get(u):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
        except Exception as e: time.sleep(3*(i+1))
Q=json.load(open('tools/queries.json')); out={}
os.makedirs('candidates',exist_ok=True)
for k,q in Q.items():
    p={'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':q+' filetype:bitmap','gsrlimit':30,
       'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':480}
    d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)) or b'{}')
    c=[]
    for pg in d.get('query',{}).get('pages',{}).values():
        ii=pg['imageinfo'][0]; w,h=ii['width'],ii['height']
        if w<2000 or w<h*1.2: continue
        m=ii.get('extmetadata',{})
        c.append({'title':pg['title'][5:],'w':w,'h':h,'idx':pg.get('index',99),'thumb':ii['thumburl'],
          'license':m.get('LicenseShortName',{}).get('value',''),'artist':m.get('Artist',{}).get('value','')})
    c=sorted(c,key=lambda x:x['idx'])[:8]
    os.makedirs('candidates/'+k,exist_ok=True)
    for i,x in enumerate(c):
        b=get(x['thumb'])
        if b: open(f'candidates/{k}/{i}.jpg','wb').write(b)
        time.sleep(0.5)
    out[k]=c; print(k,len(c),flush=True)
json.dump(out,open('candidates/index.json','w'),indent=1)
