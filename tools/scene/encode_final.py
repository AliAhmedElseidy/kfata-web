"""Encode the approved full 168-frame render; no interpolation or upscaling."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('frames', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
frames=args.frames.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
if not all((frames/f'frame-{n:04}.png').is_file() for n in range(1,169)):
    raise SystemExit('All 168 original rendered frames are required.')
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
manifest={'duration_seconds':7,'fps':24,'render_samples':16,'original_frames':168,'files':{}}
for name,width,height,quality in [('desktop',1280,720,21),('mobile',960,540,23)]:
    target=output/(name+'.mp4')
    subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate','24','-start_number','1','-i',str(frames/'frame-%04d.png'),'-frames:v','168','-vf',f'scale={width}:{height}:flags=lanczos:out_color_matrix=bt709,setsar=1','-c:v','libx264','-threads','4','-preset','slow','-crf',str(quality),'-profile:v','high','-level','3.1','-pix_fmt','yuv420p','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-color_range','tv','-movflags','+faststart','-an',str(target)],check=True)
    metadata=next(imageio_ffmpeg.read_frames(str(target)))
    assert metadata['size']==(width,height),metadata
    assert metadata['fps']==24 and abs(metadata['duration']-7)<.05,metadata
    decoded=subprocess.run([ffmpeg,'-hide_banner','-i',str(target),'-map','0','-f','null','-'],capture_output=True,check=True)
    assert 'Audio:' not in decoded.stderr.decode(errors='replace')
    manifest['files'][name+'.mp4']={'width':width,'height':height,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'codec':metadata['codec'],'audio_tracks':0}
poster=Image.open(frames/'frame-0168.png').convert('RGB')
assert poster.size==(1280,720),poster.size
poster.save(output/'poster.jpg',quality=93,optimize=True)
poster.resize((960,540),Image.Resampling.LANCZOS).save(output/'poster-mobile.jpg',quality=90,optimize=True)
for name in ['poster.jpg','poster-mobile.jpg']:
    file=output/name
    manifest['files'][name]={'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
