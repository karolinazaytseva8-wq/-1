import sys,pathlib,subprocess
from PIL import Image,ImageDraw
name=sys.argv[1];out=Image.new('RGB',(1440,900));d=ImageDraw.Draw(out)
for i,t in enumerate([.5,5,10,15,20,25,30,35,39]):
 p=pathlib.Path(f'original-review-{i}.jpg');subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',name+'.mp4','-frames:v','1','-vf','scale=480:270',str(p)],check=True);x=i%3*480;y=i//3*300;out.paste(Image.open(p),(x,y));d.text((x+5,y+272),f'{name} {t}s')
out.save('review-original-'+name+'.jpg')
