# ---------------------------------------- 
# file: make_environment.py
# author: coppermouse
# ----------------------------------------

import pygame

def height_map_value_to_z( v ):
    return v//16 - 18


def make_environment():

    world = pygame.image.load( 'world.png' )
    height = pygame.image.load( 'height.png' )

    f = size_factor = 0.01

    polygons = list()
    colors = list()

    assert world.get_size() == height.get_size()

    for x in range( world.get_size()[0] ):
        for y in range( world.get_size()[1] ):
            z = height_map_value_to_z( height.get_at( (x,y) ).r )

            for offsets, delta in [
                ( [ (0,0,0),  (1,0,0),  (1,1,0),  (0,1,0)  ], None ),
                ( [ (0,0,-1), (1,0,-1), (1,0,0),  (0,0,0)  ], [0,-1] ),
                ( [ (0,1,0),  (1,1,0),  (1,1,-1), (0,1,-1) ], [0,1]  ),
                ( [ (1,0,-1), (1,1,-1), (1,1,0),  (1,0,0)  ], [1,0]  ),
                ( [ (0,0,0),  (0,1,0),  (0,1,-1), (0,0,-1) ], [-1,0] ),
            ]:
                dx, dy = delta if delta else (0,0)

                # only place polygon if free on the side of the cube
                try:
                    adj_height = height_map_value_to_z( height.get_at( (x+dx,y+dy)  ).r )
                    if adj_height != z -1 and delta is not None: continue
                except IndexError:
                    pass

                colors.append(
                    pygame.Color( world.get_at( (x,y) )).lerp( 
                        'black', 0.5 if delta is not None else 0 ))

                polygon = list()
                polygons.append( polygon )

                for dx, dy, dz in offsets:
                    polygon.append(( (x+dx)*f, (y+dy)*f, (z+dz)*f ))

    colors = [ tuple(c)[:3] for c in colors ]

    return polygons, colors


