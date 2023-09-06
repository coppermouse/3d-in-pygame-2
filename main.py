# ---------------------------------------- 
# file: main.py
# author: coppermouse
# ----------------------------------------

import asyncio
import pygame
import numpy as np
import math
import time
import random

def rotate( vertices, axis, theta ):
    # rotates (in place, no copy) a set of verticies

    # ( n, 2) float64
    shape, dtype = vertices.shape, vertices.dtype
    assert ( len(shape) == 2 ) and shape[1] == 3 and dtype == np.float64

    # I based this code on numpy-stl rotation logic.
    # I wouldn't know how to figure out this math myself.

    # --- calc rotation matrix
    axis = np.asarray(axis)
    theta = 0.5 * np.asarray(theta)
    axis = axis / np.linalg.norm(axis)

    a = math.cos(theta)
    b, c, d = - axis * math.sin(theta)
    angles = a, b, c, d
    powers = [x * y for x in angles for y in angles]
    aa, ab, ac, ad = powers[0:4]
    ba, bb, bc, bd = powers[4:8]
    ca, cb, cc, cd = powers[8:12]
    da, db, dc, dd = powers[12:16]

    rotation_matrix = np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])
    # ---

    vertices[:] = vertices[:].dot( rotation_matrix )


async def main():
    
    _quit = False

    screen_side_size = 800
    hsss = screen_side_size // 2

    screen = pygame.display.set_mode( (screen_side_size,)*2 )
    clock = pygame.time.Clock()
    fps = 60

    pygame.font.init()
    font = pygame.font.SysFont("",24)

    world = pygame.image.load('world.png').convert() 
    
    # --- make field
    field = list()
    for x in range( world.get_size()[0] + 1 ):
        for y in range( world.get_size()[1] + 1 ):
            field.append( ( x, y, -5 + random.randrange(0,2) ))
    field = np.array( field )
    assert field.dtype == np.int64
    # ---

    # camera direction and position vectors (they are both 2d-vectors, they doesn't take the 
    # z-axis into account)
    position = pygame.math.Vector2()
    direction = pygame.math.Vector2( (0,1) )

    # performance time containers
    steps = { i:0 for i in range(5) }

    while not _quit:

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or ( ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE ):
                _quit = True

        # --- step 0: handle movement and get visible vertices
        j = time.time()
        if pygame.key.get_pressed()[ pygame.K_w ]:
            position += direction * 0.1
        if pygame.key.get_pressed()[ pygame.K_a ]:
            direction.rotate_ip(1)
        if pygame.key.get_pressed()[ pygame.K_d ]:
            direction.rotate_ip(-1)
        
        angle = math.radians( direction.angle_to((1,0)) ) + math.pi*1.5

        p3d = position_3d = list(position) + [0]

        visible_field = field[ 
            ( np.absolute( ( np.arctan2( (field - p3d)[:,0],  (field-p3d )[:,1]  ) + np.pi - angle )   ) < 1.26)
            |
            ( np.absolute( ( np.arctan2( (field - p3d)[:,0],  (field-p3d )[:,1]  ) + np.pi * 3 - angle )   ) < 1.26)
        ]
        steps[0] += (time.time() - j) 
        # ---


        # --- step 1: setup vertex to index dict
        j = time.time()
        vertex_index = { tuple(k[:2]): e for e, k in enumerate( visible_field ) }
        steps[1] += (time.time() - j) 
        # ---
        

        # --- step 2: project to 2d
        j = time.time()
        visible_field = visible_field - p3d 
        rotate( visible_field, (0,0,1), -math.radians( direction.angle_to((0,-1)) ))

        ovf =  visible_field + (0,-1.5,0)
        numpy_projection = np.flip(np.rot90(np.concatenate((
            np.array([ ovf[:,2] / ovf[:,1] ]),
            np.array([ ovf[:,0] / ovf[:,1] ])
        )))) * hsss + hsss

        steps[2] += (time.time() - j) 
        # ---


        # --- step 3: build polygons
        j = time.time()
        polygons = list()
        
        #for e, point in enumerate(numpy_projection):
        #    screen.set_at( [ point[i] * 400 + 400 for i in range(2) ], e*200 )

        for a,b in vertex_index.items():

            polygon = [ numpy_projection[b] ]
                
            for dx,dy in [(1,0),(1,1),(0,1)]:
                adj = a[0] + dx, a[1] + dy
                try:
                    p = numpy_projection[vertex_index[adj]]
                    polygon.append(p)
                except KeyError:
                    break
            else:
                polygons.append( (polygon, world.get_at(a)) )
        steps[3] += (time.time() - j) 
        # ---


        # --- step 4: render view (include visual for debug)
        j = time.time()
        screen.fill(0)
        for polygon, color in polygons:
            pygame.draw.polygon( screen, color, polygon )


        screen.blit( font.render('fps: {0}'.format( clock.get_fps()  ),True, 'white'), (0,10) )

        for e, color in enumerate([ 'blue', 'red', 'green', 'yellow', 'magenta' ]):
            pygame.draw.rect( screen, color, (0,40+e*20,steps[e]*10,20) )

        steps[4] += (time.time() - j) 
        # ---


        clock.tick(fps)
        pygame.display.update()
        await asyncio.sleep(0)


asyncio.run( main() )


