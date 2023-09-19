# Example file showing a basic pygame "game loop"
import pygame
import numpy as np
# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True


points = list()
for x in range(32):
    for y in range(32):
        for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            points.append( 
                ( x*0.02+dx*0.01, y*0.02+dy*0.01, 0 )  
            )





colors = [
    hash(str(i)) for i in range(len(points)//4)
]


lpoints = np.array(points)
colors = np.array(colors)

def j(p, colors):



    points = [[-1,-2,0,1,2,3,5,8], [-3,-4,0,-3,5,9,2,1]]
    points = np.array(points)


    x2 = p[:,:,0]
    x = np.array(points[0,:])
    y = np.array(points[1,:])

    mask = np.logical_and(np.logical_and(x>=0, x<=5), np.logical_and(y>=0, y<=5))
    # mask = array([False, False,  True, False,  True, False,  True, False])

    mask2 = np.logical_and(x2>-1, x2<500)
    mask3 = np.logical_and(p[:,:,0]>=-1, p[:,:,0] <= 1)
    j = mask3.any(axis=1)
    p = p[ j ]
    a = p
    b = colors[j]
    return a,b
    x2 = x2[mask2]
    x = x[mask] # x = array([0, 2, 5])
    y = y[mask] # y = array([0, 5, 2])


f = 0

def p(lpoints, colors):
    global f
    points = lpoints + (f,0,0)

    polygons = points.reshape( len(points)//4,4,3 )

    projected_polygons = (polygons[:,:,:2])
    
    projected_polygons, colors = j(projected_polygons, colors)
    projected_polygons = projected_polygons * 400 + 400
    return projected_polygons, colors


import time


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    f += 0.001
    jk = time.time()
    projected_polygons, lcolors = p(lpoints, colors)
    print(jk-time.time())
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE


    jk = time.time()
    for polygon, color in zip(projected_polygons, lcolors):
        pygame.draw.polygon( screen, int(color), polygon )
        #screen.set_at( tuple(map(int,point[:2])), 'white')
        pass
    print(":::",jk-time.time())


    screen.set_at( (400,400), 'cyan' )
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(600)  # limits FPS to 60
    print(clock.get_fps())

pygame.quit()
