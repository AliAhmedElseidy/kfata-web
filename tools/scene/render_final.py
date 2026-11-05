"""Optional future reproduction; do not run alongside an existing scene render."""
import argparse
import sys
from pathlib import Path
import bpy

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_start=1;scene.frame_end=168;scene.frame_step=1
scene.cycles.samples=16
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.08
scene.cycles.adaptive_min_samples=4
scene.cycles.use_denoising=True
scene.render.filepath=str(output/'frame-')
bpy.ops.render.render(animation=True)
