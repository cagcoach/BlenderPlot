# This example assumes we have a mesh object selected

import bpy
import bmesh
import numpy as np
import random

import numpy
import scipy.io

rootDir= '/media/remote_home/cgrund/Downloads/'

file = 'gt_256x256x32_11_000050.mat'

print(rootDir + file)
data = scipy.io.loadmat( rootDir + file)['data'] 

print(data.shape)
voxel_dims = np.array([256, 256, 32])
data = np.reshape(data, (voxel_dims))
data = np.transpose(data, (1, 0, 2))
context = bpy.context
scene = context.scene

def generate_blocks(scn,points,name="MyObject"):
    mesh = bpy.data.meshes.new("mesh")  # add a new mesh
    obj = bpy.data.objects.new(name, mesh)
    scene = bpy.context.scene
    scene.objects.link(obj)  # put the object into the scene (link)
    scene.objects.active = obj
    obj.select = True  # select object
    mesh = bpy.context.object.data
    bm = bmesh.new()
    #                     0          1       2         3         4         5       6        7
    block=np.array([ [-1,-1,-1],[-1,-1,1],[-1,1,-1],[-1,1,1],[1,-1,-1],[1,-1,1],[1,1,-1],[1,1,1]]).astype(float)
    block*=0.4
    verts = np.empty(shape=(0,3))
    for i in points:
        #print((block+i).shape)
        verts=np.append(verts, (block+i),axis=0)
        
    #print(verts)
    for v in verts:
        bm.verts.new(v)
    bm.to_mesh(mesh)
    bm.verts.ensure_lookup_table()
    for i in range(0,len(bm.verts),8):
        bm.faces.new( [bm.verts[i+0], bm.verts[i+1],bm.verts[i+3], bm.verts[i+2]])
        bm.faces.new( [bm.verts[i+4], bm.verts[i+5],bm.verts[i+1], bm.verts[i+0]])
        bm.faces.new( [bm.verts[i+6], bm.verts[i+7],bm.verts[i+5], bm.verts[i+4]])
        bm.faces.new( [bm.verts[i+2], bm.verts[i+3],bm.verts[i+7], bm.verts[i+6]])
        bm.faces.new( [bm.verts[i+5], bm.verts[i+7],bm.verts[i+3], bm.verts[i+1]]) #top
        bm.faces.new( [bm.verts[i+0], bm.verts[i+2],bm.verts[i+6], bm.verts[i+4]]) #bottom
    if bpy.context.mode == 'EDIT_MESH':
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
    obj.data.update()
    bm.free
    return obj


def clear_scene(scene):
    #Clears the current scene
    for obj in scene.objects:
        scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return

def base_object():
    #Creates base cube
    bpy.ops.mesh.primitive_cube_add(radius=0.4, location=(0,0,0))
    return scene.objects.active

def norm_color(color):
    return color

#Set the colors for the classes
colors = {  '_3':(0.392157,0.588235,0.960784),
	 '_4':(0.392157,0.901961,0.960784),
	 '_5':(0.392157,0.313725,0.980392),
	 '_6':(0.117647,0.235294,0.588235),
	 '_7':(0.000000,0.000000,1.000000),
	 '_8':(0.313725,0.117647,0.705882),
	 '_9':(0.000000,0.000000,1.000000),
	 '_10':(1.000000,0.117647,0.117647),
	 '_11':(1.000000,0.156863,0.784314),
	 '_12':(0.588235,0.117647,0.352941),
	 '_13':(1.000000,0.000000,1.000000),
	 '_14':(1.000000,0.588235,1.000000),
	 '_15':(0.294118,0.000000,0.294118),
	 '_16':(0.686275,0.000000,0.294118),
	 '_17':(1.000000,0.784314,0.000000),
	 '_18':(1.000000,0.470588,0.196078),
	 '_19':(1.000000,0.588235,0.000000),
	 '_20':(0.588235,1.000000,0.666667),
	 '_21':(0.000000,0.686275,0.000000),
	 '_22':(0.529412,0.235294,0.000000),
	 '_23':(0.588235,0.941176,0.313725),
	 '_24':(1.000000,0.941176,0.588235),
	 '_25':(1.000000,0.000000,0.000000),
	 '_26':(0.196078,1.000000,1.000000),
	 '_27':(0.392157,0.588235,0.960784),
	 '_28':(0.000000,0.000000,1.000000),
	 '_29':(1.000000,0.156863,0.784314),
	 '_30':(1.000000,0.117647,0.117647),
	 '_31':(0.588235,0.117647,0.352941),
	 '_32':(0.392157,0.313725,0.980392),
	 '_33':(0.313725,0.117647,0.705882),
	 '_34':(0.000000,0.000000,1.000000)
        }
color_map = {
    10: '_3',
	20: '_9',
	30: '_10',
	40: '_13',
	50: '_17',
	70: '_21',
	80: '_24',
            }

def creatematerial(name, col):
    color = norm_color(col)
    red = color[0]
    green = color[1]
    blue = color[2]
    alpha = 1.0
    mat=(bpy.data.materials.new(name=name))    
    mat.use_nodes = True
    Diffuse_BSDF = mat.node_tree.nodes['Diffuse BSDF']
    Diffuse_BSDF.inputs[0].default_value = [red, green, blue, alpha]
    mat.diffuse_color = [red, green, blue]
    return mat

#Delete all objects in the scene. THIS IS SLOW FOR MANY OBJECTS! So, take a new only containing the default cube istead of an already used voxel scene.
clear_scene(scene)

bpy.context.scene.render.engine = 'CYCLES'

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
empty = bpy.context.active_object

materials=dict()    

for k,v, in colors.items():
    materials[k] = creatematerial(k,v)

for label in color_map:
    print(label)

    col = colors[ color_map[label] ]
    col = norm_color(col)
    xx, yy, zz = numpy.where(data == label)
    points=[[xx[i], -yy[i], zz[i]] for i in range(len(xx))]
    obj=generate_blocks(scene,points,"Label {}".format(label))
    obj.data.materials.clear()
    obj.data.materials.append(materials[color_map[label]])
    obj.parent=empty
        
bpy.ops.object.camera_add(location=(-50,95,55),rotation=(1.18683,0,4)) #Set camera location
bpy.context.object.data.clip_end = np.max(np.max(data))*4 #Extend Clip length so that far away voxels are plotted aswell
point=bpy.ops.object.lamp_add(type='POINT',location=(15,15,60)) 
bpy.ops.object.lamp_add(type='SUN',location=(15,15,80))
#The sun intensity needs to be adjusted afterwords manually. If someone can automate this feel free to make a push request.

#Make background transparent
bpy.context.scene.cycles.film_transparent = True

bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.cycles.samples = 256
#Set output respolution
bpy.context.scene.render.resolution_x = 2560
bpy.context.scene.render.resolution_y = 1440
bpy.context.scene.cycles.device = 'GPU' #If you have no GPU support, comment this!