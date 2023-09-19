# Example file showing a basic pygame "game loop"
import pygame
import numpy as np
# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True


points = list()
for p in [(0.2,0.2),(0.4,0.5)]:
    x,y = p
    for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]:
        points.append( (x+dx*0.1,y+dy*0.1,0)  )

assert len(points) == 8


lpoints = np.array(points)


colors = [

    hash(str(i)) for i in range(2)

]

points = lpoints + (0.8,0,0)

polygons = points.reshape( 2,4,3 )

projected_polygons = (polygons[:,:,:2])



def j(p):
    points = [[-1,-2,0,1,2,3,5,8], [-3,-4,0,-3,5,9,2,1]]
    points = np.array(points)


    x2 = p[:,:,0]
    print(x2)
    x = np.array(points[0,:])
    y = np.array(points[1,:])

    mask = np.logical_and(np.logical_and(x>=0, x<=5), np.logical_and(y>=0, y<=5))
    # mask = array([False, False,  True, False,  True, False,  True, False])

    mask2 = np.logical_and(x2>-1, x2<500)
    mask3 = np.logical_and(p[:,:,0]>=-1, p[:,:,0] <= 1)
    j = mask3.any(axis=1)
    print(j)
    p = p[ j ]
    return p
    x2 = x2[mask2]
    x = x[mask] # x = array([0, 2, 5])
    y = y[mask] # y = array([0, 5, 2])


projected_polygons = j(projected_polygons)

projected_polygons = projected_polygons * 400 + 400
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE

    for point in points + (400,400,0):
        screen.set_at( tuple(map(int,point[:2])), 'white')

    print(len(projected_polygons))
    for polygon, color in zip(projected_polygons, colors):
        pygame.draw.polygon( screen, color, [ p for p in polygon ] )
        #screen.set_at( tuple(map(int,point[:2])), 'white')
        pass


    screen.set_at( (400,400), 'cyan' )
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
