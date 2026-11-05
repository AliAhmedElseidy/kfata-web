"""Original architectural concept, offline Blender render only.

Not a KFATA project. No external models/textures/reference-video frames.
Usage: blender -b -t 4 --python tools/scene/build_concept.py -- --output ABS_DIR
Render chosen frames with Blender -f, or the complete sequence with -a.
"""
import argparse
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

args = argparse.ArgumentParser()
args.add_argument('--output', required=True)
args = args.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 12
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 168
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(out / 'frames' / 'frame-')
(out / 'frames').mkdir(exist_ok=True)
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.32, .39, .42, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .35
scene.view_settings.view_transform = 'AgX'

def material(name, color, metallic=0, roughness=.5, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return mat

stone = material('Warm limestone', (.64, .52, .36), roughness=.72)
plaster = material('Ivory mineral plaster', (.78, .73, .62), roughness=.8)
concrete = material('Structural concrete', (.37, .39, .37), roughness=.9)
bronze = material('Brushed dark bronze', (.12, .085, .048), metallic=.72, roughness=.3)
glass = material('Smoked reflective glazing', (.055, .115, .135), metallic=.7, roughness=.17)
soil = material('Site earth', (.23, .21, .17), roughness=1)
green = material('Garden planting', (.12, .21, .12), roughness=.9)
wood = material('Timber fins', (.24, .105, .045), roughness=.55)
light_mat = material('Warm architectural light', (1, .56, .19), emission=4)
water = material('Courtyard reflecting water', (.07, .18, .19), metallic=.6, roughness=.12)

def emerge(obj, start, end, axis=2):
    final = obj.scale.copy()
    obj.hide_render = True
    obj.keyframe_insert('hide_render', frame=max(1, start - 1))
    obj.hide_render = False
    obj.keyframe_insert('hide_render', frame=start)
    base = obj.location.copy()
    half = obj.dimensions[axis] / 2
    obj.scale[axis] = .002
    obj.location[axis] = base[axis] - half
    obj.keyframe_insert('scale', frame=start)
    obj.keyframe_insert('location', frame=start)
    obj.scale = final
    obj.location = base
    obj.keyframe_insert('scale', frame=end)
    obj.keyframe_insert('location', frame=end)

def box(name, xyz, size, mat, start=0, end=0, axis=2, bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft masonry edges', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    if start:
        emerge(o, start, end, axis)
    return o

# Visible pads and frame become a coherent two-storey courtyard building.
box('Site plinth', (0, 0, -.3), (19, 14, .4), soil, bevel=.12)
box('Approach paving', (0, -4.6, -.06), (16.5, 4.2, .14), stone, 8, 22)
for ix, x in enumerate([-5, 0, 5]):
    for iy, y in enumerate([-2, 1, 4]):
        n = ix * 3 + iy
        box('Foundation pad', (x, y, .06), (1.3, 1.3, .35), concrete, 2+n, 16+n)
        box('Ground structural column', (x, y, 1.65), (.28, .28, 3), concrete, 19+n, 39+n)
        box('Upper structural column', (x, y, 4.7), (.26, .26, 2.8), concrete, 47+n, 65+n)
box('Ground floor slab', (0, 1, .31), (11.5, 7, .22), concrete, 14, 30, 0)
box('First floor slab', (0, 1, 3.26), (11.8, 7.4, .25), plaster, 39, 56, 0)
box('Roof slab', (0, 1, 6.22), (12.2, 7.6, .25), plaster, 62, 77, 0)
# Quiet solid planes frame the large glazed openings rather than a generic cube.
for x in [-5.55, 5.55]:
    box('Side limestone wall', (x, 1.1, 1.8), (.35, 6.9, 2.8), stone, 69, 87)
    box('Upper side wall', (x, 1.1, 4.75), (.35, 6.9, 2.8), plaster, 75, 93)
box('Rear wall', (0, 4.45, 1.8), (11.1, .25, 2.8), plaster, 68, 86, 0)
box('Upper rear wall', (0, 4.45, 4.75), (11.1, .25, 2.8), stone, 76, 94, 0)
box('Entrance stone pier', (2.15, -2.42, 1.78), (2.1, .35, 2.75), stone, 80, 98)
box('Upper cantilever fascia', (0, -2.8, 5.99), (12.2, .3, .58), plaster, 91, 108, 0)
box('Lower shadow fascia', (0, -2.85, 3.22), (11.8, .28, .3), bronze, 93, 109, 0)
box('Timber entrance door', (2.0, -2.65, 1.58), (1.35, .16, 2.4), wood, 92, 107)
for level, z in enumerate([1.8, 4.7]):
    xs = [-4.6, -3.2, -1.8, -.4, 1.0, 2.4, 3.8, 5.0] if level else [-4.6,-3.2,-1.8,-.4,3.8,5.0]
    for i, x in enumerate(xs):
        box('Full height glazed panel', (x, -2.48, z), (1.28, .07, 2.5), glass, 96+i, 112+i, 0)
        box('Bronze glazing mullion', (x-.67, -2.55, z), (.055, .10, 2.57), bronze, 100+i, 116+i)
    box('Glazing head rail', (0, -2.55, z+1.28), (11.1, .10, .055), bronze, 105, 120, 0)
for i in range(12):
    box('Upper timber sun fin', (3.2+i*.2, -2.74, 4.74), (.06, .32, 2.5), wood, 109+i//2, 125+i//2)
# Facade coursing and approach steps.
for z in [.8,1.4,2,2.6]:
    box('Stone joint', (2.15,-2.607,z), (2.1,.012,.012), bronze, 112, 126, 0, bevel=0)
for i in range(3):
    box('Arrival step', (1.7,-3.1-i*.38,.25-i*.07), (3.5,.5,.14), stone, 116+i*2, 131+i*2)
box('Reflecting pool rim', (-3.5,-4.8,.02), (5.3,2.1,.16), plaster, 119, 134)
box('Reflecting pool', (-3.5,-4.8,.13), (5,1.8,.05), water, 123, 138, 0)
for x in [-7.1, 7.1]:
    box('Raised garden planter', (x,0,.12), (1.6,7.2,.3), stone, 122, 136)
    for i in range(7):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=.6, location=(x,-2.6+i,.65))
        o=bpy.context.object; o.name='Low garden planting'; o.scale=(.8,.8,.65);o.data.materials.append(green)
        emerge(o,128+i,141+i)
for z in [3.08,5.66]:
    box('Warm facade linear light', (0,-2.66,z), (10.7,.035,.035), light_mat, 134, 148, 0)
for x in [-5,0,5]:
    bpy.ops.object.light_add(type='AREA', location=(x,-3,2.9))
    o=bpy.context.object; o.name='Warm arrival light';o.rotation_euler=(0,0,0);o.data.shape='DISK';o.data.size=2
    o.data.color=(1,.65,.35);o.data.energy=0;o.data.keyframe_insert('energy',frame=132)
    o.data.energy=85;o.data.keyframe_insert('energy',frame=150)

# Soft sun and large fill. Original camera, no external environment image.
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(28), math.radians(-22), math.radians(-28)))
bpy.context.object.data.energy=2.1;bpy.context.object.data.angle=.12
bpy.ops.object.light_add(type='AREA', location=(0,-7,12))
bpy.context.object.data.energy=1100;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=9
bpy.context.object.rotation_euler=(Vector((0,0,2))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(18,-24,14))
camera=bpy.context.object;scene.camera=camera
camera.rotation_euler=(Vector((0,0,2))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=23.5
camera.keyframe_insert('location',frame=1)
camera.location=(17,-23.3,13.6)
camera.rotation_euler=(Vector((0,0,2))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.keyframe_insert('location',frame=168)
camera.keyframe_insert('rotation_euler',frame=168)
scene.frame_set(168)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'kfata-concept.blend'))
print('ORIGINAL_SCENE_READY',out)
