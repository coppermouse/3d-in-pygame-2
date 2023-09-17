import time
import pygame
import numpy as np

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True

# setup points (n, 3), every 4-th point is a new polygon
points = list()
f = 0.01
for x in range(32):
    for y in range(32):
        for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            points.append( 
                ( x*f*2 + dx*f, y*f*2 + dy*f, 0 ))

colors = [
    hash(str(i)) for i in range( len(points)//4 )
]


points = np.array(points)
colors = np.array(colors)

def filter_projected_polygons_out_of_view(projected_polygons, colors):

    pp = projected_polygons
    assert pp.shape[1] == 4 and pp.shape[2] == 2

    mask = np.logical_and(
        np.logical_and( pp[:,:,0]>=-1, pp[:,:,0] <= 1),
        np.logical_and( pp[:,:,1]>=-1, pp[:,:,1] <= 1),
    ).any( axis = 1 ) 
    
    return pp[ mask ], colors[ mask ]



def projection( lpoints, colors, offset ):
    points = lpoints + ( *offset, 0 )

    polygons = points.reshape( len(points)//4, 4, 3 )

    projected_polygons = (polygons[:,:,:2])
    
    projected_polygons, colors = filter_projected_polygons_out_of_view( projected_polygons, colors )
    projected_polygons = projected_polygons * 400 + 400
    return projected_polygons, colors


offset = np.array([0.0,0.0])

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for k, delta in (
        (pygame.K_d,(1,0)),  
        (pygame.K_a,(-1,0)),  
        (pygame.K_w,(0,-1)),  
        (pygame.K_s,(0,1)),  
    ):
        if pygame.key.get_pressed()[k]:
            offset += np.array(delta) * 0.01

    jk = time.time()
    projected_polygons, filtered_colors = projection( points, colors, offset )
    #print(jk-time.time())
    
    screen.fill("black")

    jk = time.time()
    for polygon, color in zip( projected_polygons, filtered_colors ):
        pygame.draw.polygon( screen, int(color), polygon )

    screen.set_at( (400,400), 'cyan' )
    pygame.display.flip()

    clock.tick(600)
    print(clock.get_fps())


pygame.quit()


