# ---------------------------------------- 
# file: projection.py
# author: coppermouse
# ----------------------------------------

import math
import numpy as np
from rotate import rotate

def filter_projected_polygons_out_of_view( projected_polygons, colors ):
    pp = projected_polygons
    assert pp.shape[1] == 4 and pp.shape[2] == 2

    assert projected_polygons.shape[0] == colors.shape[0], (projected_polygons.shape[0], colors.shape[0])

    mask = np.logical_and(
        np.logical_and( pp[:,:,0]>=-1, pp[:,:,0] <= 1),
        np.logical_and( pp[:,:,1]>=-1, pp[:,:,1] <= 1),
    ).any( axis = 1 ) 
    
    return pp[ mask ], colors[ mask ]


def filter_polygons_based_on_near( polygons, offset, colors, camera_vector, near ):
    mask = np.logical_and( 
        (polygons-(list(offset)+[0]))[:,0].dot( camera_vector ) > -near[1] ,
        (polygons-(list(offset)+[0]))[:,0].dot( camera_vector ) < -near[0] ,
    )
    return polygons[ mask ], colors[ mask ]


def fogify( colors, fog, factors):
    assert colors.shape[0] == factors.shape[0]
    assert colors.shape[1] == 3
    assert len(colors.shape) == 2
    assert fog.shape == (3,)
    assert len(factors.shape) == 1
    return colors + ( fog - colors ) * np.clip( factors.reshape( factors.shape[0], 1 ) * 2, 0, 1)


def projection( polygons, colors, offset, theta, projection_factor, projection_offset, near, view_mode, fog_color ):

    camera_vector = [ math.sin( theta ), math.cos( theta ), 0 ]

    near_polygons, colors = filter_polygons_based_on_near(
        polygons, offset, colors, camera_vector, near )

    nps = near_points = near_polygons.reshape( len( near_polygons )*4, 3 ) - ( *offset, 0 )
    rotate( near_points, (0,0,1), -theta)

    near_polygons = near_points.reshape( len( near_points )//4, 4, 3 )

    if view_mode == 0:
        projected_polygons = (near_polygons[:,:,:2]) * projection_factor * (-1,1) + projection_offset

        return projected_polygons, colors

    elif view_mode == 1:
        rotate( near_points, (1,0,0), 0.3)
        
        projected_polygons = np.flip( np.rot90( np.concatenate((
            np.array([ nps[:,2] / nps[:,1] ]),
            np.array([ nps[:,0] / nps[:,1] ])
        )))).reshape( len( nps )//4, 4, 2 )


        flat = projected_polygons.reshape( len( near_points )//4, 8 )
        front_mask = (
            (( flat[:,2] - flat[:,0]) * ( flat[:,3] + flat[:,1])) +
            (( flat[:,4] - flat[:,2]) * ( flat[:,5] + flat[:,3])) +
            (( flat[:,6] - flat[:,4]) * ( flat[:,7] + flat[:,5])) +
            (( flat[:,0] - flat[:,6]) * ( flat[:,1] + flat[:,7]))
        ) > 0

        flat = flat[ front_mask ]
        projected_polygons = flat.reshape( flat.shape[0], 4, 2 )

        fog = np.array( fog_color )
        
        # TODO: to make projection faster we could move fogify to a later step. now it is a bit
        #       hard to do that.
        colors = fogify( colors, fog, np.linalg.norm( -near_polygons[:,0], axis = 1 ) )

        colors = colors[ front_mask ]

        projected_polygons, colors = filter_projected_polygons_out_of_view( projected_polygons, colors )
        projected_polygons = projected_polygons * projection_factor + projection_offset

        return projected_polygons, colors


