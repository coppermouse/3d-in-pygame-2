import time
import pygame
import numpy as np
import math

pygame.init()
screen = pygame.display.set_mode(
    (1920//2, 1080//2), 
    #pygame.SCALED | pygame.NOFRAME 
)
clock = pygame.time.Clock()
running = True

world = pygame.image.load('world.png')
height = pygame.image.load('height.png')

# setup points (n, 3), every 4-th point is a new polygon
polygons = list()
colors = list()
f = 0.01
for x in range(32):
    for y in range(32):
        colors.append( world.get_at( (x,y) ))
        z = (height.get_at((x,y)).r)//16

        z -= 18

        polygon = list()
        polygons.append(polygon)
        for dx, dy in [(0,0),(1,0),(1,1),(0,1)]:
            polygon.append( 
                ( x*f + dx*f, y*f + dy*f, z*f ))

        for s in [0]:
            for h,d in [
                ( [(0,0,0),(1,0,0),(1,0,-1),(0,0,-1)][::-1], [ 0,  -1]  ),
                ( [(0,1,0),(1,1,0),(1,1,-1),(0,1,-1)][:: 1], [ 0,  1]   ),
                ( [(1,0,0),(1,1,0),(1,1,-1),(1,0,-1)][::-1], [  1, 0]  ),
                ( [(0,0,0),(0,1,0),(0,1,-1),(0,0,-1)][:: 1], [  -1,  0]  ),
            ]:
                dx, dy = d
                try:
                    adj_height = height.get_at( (x+dx,y+dy)  ).r//16 - 18
                    if adj_height != z -1: continue
                except IndexError:
                    pass


                colors.append( pygame.Color(world.get_at( (x,y) )).lerp('black',0.5)  )
                polygon = list()
                polygons.append(polygon)
                for dx, dy, dz in h:
                    polygon.append( 
                        ( x*f + dx*f, y*f + dy*f, z*f+dz*f ))

l = list(zip(polygons,colors))

print(len(polygons))
#quit()

l.sort( key=lambda a:a[0][0][2]+a[0][1][2]+a[0][2][2]+a[0][3][2])

#colors = [
#    hash(str(i)) for i in range( len(points)//4 )
#]


polygons = [ c[0] for c in l ]
colors = [ c[1] for c in l ]

polygons = np.array(polygons)
b = 0.16
polygons -= (b,b,0)
colors = np.array(colors)

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




def filter_projected_polygons_out_of_view(projected_polygons, colors):

    pp = projected_polygons
    assert pp.shape[1] == 4 and pp.shape[2] == 2

    assert projected_polygons.shape[0] == colors.shape[0], (projected_polygons.shape[0], colors.shape[0])

    mask = np.logical_and(
        np.logical_and( pp[:,:,0]>=-1, pp[:,:,0] <= 1),
        np.logical_and( pp[:,:,1]>=-1, pp[:,:,1] <= 1),
    ).any( axis = 1 ) 
    
    a = pp[ mask ]
    b = colors[ mask ]
    return a,b


def filter_polygons_based_on_near( polygons, offset, colors, camera_vector ):
    mask = np.logical_and( 
        #(polygons-(list(offset)+[0]))[:,0].dot( camera_vector ) > -0.1 ,
        True,
        (polygons-(list(offset)+[0]))[:,0].dot( camera_vector ) < -0.025 ,
    )
    return polygons[mask], colors[mask]


    

def projection( polygons, colors, offset, theta ):

    camera_vector = [math.sin(theta), math.cos(theta),0]

    polygons, colors = filter_polygons_based_on_near( polygons, offset, colors, camera_vector )

    lpoints = polygons.reshape( len(polygons)*4, 3 )

    #lpoints = lpoints[ ( lpoints - (0,0,0) ).dot( (1,0,0) ) > 0 ]

    points = lpoints - ( *offset, 0 )
    rotate( points, (0,0,1), -theta)

    polygons = points.reshape( len(points)//4, 4, 3 )
    #polygons, colors = filter_polygons_based_on_bfc( polygons, colors, camera_vector, normals )
    if 0:
        polygons = points.reshape( len(points)//4, 4, 3 )
        projected_polygons = (polygons[:,:,:2])
    else:
        points = polygons.reshape( len(polygons)*4, 3 )
        ovf =  points
        l = np.flip(np.rot90(np.concatenate((
            np.array([ ovf[:,2] / ovf[:,1] ]),
            np.array([ ovf[:,0] / ovf[:,1] ])
        ))))
        projected_polygons = l.reshape( len(points)//4, 4, 2 )


        p = projected_polygons.reshape( len(points)//4, 8 )
        m = (
((p[:,2] - p[:,0]) * (p[:,3] + p[:,1])) +
((p[:,4] - p[:,2]) * (p[:,5] + p[:,3])) +
((p[:,6] - p[:,4]) * (p[:,7] + p[:,5])) +
((p[:,0] - p[:,6]) * (p[:,1] + p[:,7]))
)

        m = m > 0
        p = p[m]
        p = p.reshape( p.shape[0], 4, 2 )
        colors = colors[m]


    projected_polygons, colors = filter_projected_polygons_out_of_view( p, colors )
    projected_polygons = projected_polygons * 400 + 200
    return projected_polygons, colors


camera_position = np.array([0.0,0.0])
camera_angle = math.pi

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for k, delta in (
        (pygame.K_w,-1),  
        (pygame.K_s,1),  
    ):
        if pygame.key.get_pressed()[k]:
            camera_position += np.array( [math.sin(camera_angle), math.cos(camera_angle)]  ) * 0.01 * delta



    for k, delta in (
        (pygame.K_a,1),  
        (pygame.K_d,-1),  
    ):
        if pygame.key.get_pressed()[k]:
            camera_angle += delta * 0.01


    camera_vector = pygame.math.Vector2( [math.sin(camera_angle), math.cos(camera_angle)] )
    #camera_position += (0.16,0.16)
    camera_position = camera_vector * 0.4

    jk = time.time()
    projected_polygons, filtered_colors = projection( polygons, colors, camera_position, camera_angle )
    #print(jk-time.time())
    
    screen.fill("black")

    jk = time.time()
    for polygon, color in zip( projected_polygons, filtered_colors ):
        pygame.draw.polygon( screen, color, polygon )

    screen.set_at( (400,400), 'cyan' )

    #pygame.draw.line( screen, 'cyan', (400,400), (camera_vector * 100) + (400,400) )



    pygame.display.flip()

    clock.tick(600)
    print(clock.get_fps())


pygame.quit()


