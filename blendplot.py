# This example assumes we have a mesh object selected

import bpy
import bmesh
import numpy as np
import random

import numpy
import scipy.io

rootDir= '/home/garbade/datasets/sscnet/data/mg_gt/'

file = 'NYU0077_0000.mat'

print(rootDir + file)
data = scipy.io.loadmat( rootDir + file)['label'] 

print(data.shape)
data = np.transpose(data, (0, 2, 1))
context = bpy.context
scene = context.scene

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
colors = {  '_1':(    0.8400,   0.1500,   0.1600),
            '_2':(    0.1700,   0.6300,   0.1700),
            '_3':(    0.6200,   0.8500,   0.9000),
            '_4':(    0.4500,   0.6200,   0.8100),
            '_5':(    0.8000,   0.8000,   0.3600),
            '_6':(    1.0000,   0.7300,   0.4700),
            '_7':(    0.5800,   0.4000,   0.7400),
            '_8':(    0.1200,   0.4700,   0.7100),
            '_9':(    0.7400,   0.7400,   0.1300),
            '_10':(    1.0000,   0.5000,   0.0500),
            '_11':(    0.7700,   0.6900,   0.8400)
        }
color_map = {1: '_1',
            2: '_2',
            3: '_3',
            4: '_4',
            5: '_5',
            6: '_6',
            7: '_7',
            8: '_8',
            9: '_9',
            10: '_10',
            11: '_11'
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

#Create a base object to copy from
bo = base_object()
mesh = bo.data
for label in color_map:
    print(label)

    col = colors[ color_map[label] ]
    col = norm_color(col)
    xx, yy, zz = numpy.where(data == label)
    bo.data.materials.clear()
    bo.data.materials.append (materials[color_map[label]])
    for i in range(len(xx)):
        (x,y,z) = (xx[i], -yy[i]+60, zz[i])
        thiscube = bo.copy()
        thiscube.data = thiscube.data.copy()
        scene.objects.link(thiscube)
        thiscube.location=(x,y,z)
        thiscube.parent=empty
        
#Delete the base object. It's not needed anymore
scene.objects.unlink(bo)
bpy.data.objects.remove(bo)

bpy.ops.object.camera_add(location=(-50,95,55),rotation=(1.18683,0,4)) #Set camera location
bpy.context.object.data.clip_end = 200 #Extend Clip length so that far away voxels are plotted aswell
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