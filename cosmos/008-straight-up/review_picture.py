import json,pathlib,subprocess,concurrent.futures
from PIL import Image,ImageDraw
R=pathlib.Path('.');p=json.load(open('plan.json'));part=int(__import__('sys').argv[1]);spec=p['parts'][part];shots=p['shots'][spec['first']:spec['last']];folder=R/'review'/f'group-{part:02}';folder.mkdir(parents=True,exist_ok=True)
def one(s):
 for j,f in enumerate([min(20,s['frames']//5),s['frames']//2,max(0,s['frames']-10)]):
  dest=folder/f"{s['id']:03}-{j}.jpg";subprocess.run(['ffmpeg','-v','error','-threads','1','-ss',str(f/25),'-i','render/'+s['render_key']+'.mp4','-frames:v','1','-filter_threads','1','-vf','scale=480:270','-threads','1',str(dest)],check=True)
with concurrent.futures.ThreadPoolExecutor(2) as ex:list(ex.map(one,shots))
for base in range(0,len(shots),4):
 sh=Image.new('RGB',(1440,1160));d=ImageDraw.Draw(sh)
 for i,s in enumerate(shots[base:base+4]):
  for j in range(3):sh.paste(Image.open(folder/f"{s['id']:03}-{j}.jpg"),(j*480,i*290))
  d.text((5,i*290+272),f"{s['id']:03} {s['start_frame']/25:.2f}s {s['asset']}")
 sh.save(folder/f'page-{base//4:02}.jpg')
print('All source range and timed label frames exported',part,flush=True)
