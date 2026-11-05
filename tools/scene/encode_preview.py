"""Offline encoder. Optional local dependency: imageio-ffmpeg (not server runtime)."""
import argparse
import subprocess
from pathlib import Path
import imageio_ffmpeg

parser = argparse.ArgumentParser()
parser.add_argument('directory', type=Path)
args = parser.parse_args()
root = args.directory.resolve()
frames = sorted((root / 'draft-frames').glob('frame-*.png'))
if len(frames) != 84:
    raise SystemExit(f'Expected 84 frames (1..167 step 2), found {len(frames)}')
with (root / 'encode.log').open('wb') as log:
    process = subprocess.Popen([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-f', 'image2pipe', '-vcodec', 'png',
        '-framerate', '12', '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
        '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an',
        str(root / 'construction-preview.mp4'),
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
    for frame in frames:
        process.stdin.write(frame.read_bytes())
    process.stdin.close()
    if process.wait():
        raise SystemExit('Encoding failed; inspect encode.log')
