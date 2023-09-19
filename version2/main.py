
import asyncio
import time
import pygame
import numpy as np
import math
from make_environment import make_environment
from projection import projection

pygame.init()
screen = pygame.display.set_mode(
    (1920//1, 1080//1), 
    pygame.SCALED | pygame.NOFRAME 
)
clock = pygame.time.Clock()

polygons, colors = make_environment()

pygame.font.init()

font = pygame.font.SysFont(None,30)

# --- sort the polygons based on positions, make sure colors also being sorted becuase its order correspond to polygons order
sorter = list( zip( polygons, colors ) )
sorter.sort( key = lambda a:a[0][0][2] + a[0][1][2] + a[0][2][2] + a[0][3][2] )
polygons = [ c[0] for c in sorter ]
colors = [ c[1] for c in sorter ]
# ---

# numpyify the environment
polygons = np.array( polygons )
colors = np.array( colors )[:,:3]


async def main():

    # declare camera variables
    camera_position = np.array([0.0,0.0])
    camera_angle = math.pi

    half_screen_size = np.array(screen.get_size()) // 2


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for k, delta in ( (pygame.K_w,-1), (pygame.K_s,1) ):
            if pygame.key.get_pressed()[k]:
                camera_position += np.array( [math.sin(camera_angle), math.cos(camera_angle)]  ) * 0.002 * delta



        for k, delta in ( (pygame.K_a,-1), (pygame.K_d,1) ):
            if pygame.key.get_pressed()[k]:
                camera_angle += delta * 0.05

    
        projected_polygons, filtered_colors = projection( polygons, colors, camera_position, camera_angle, half_screen_size*(1,2), half_screen_size, near=-0.5 )
    
        screen.fill( (64,68,70) )

        for polygon, color in zip( projected_polygons, filtered_colors ):
            pygame.draw.polygon( screen, color, polygon )


        f = clock.get_fps()
        screen.blit( font.render(str(f),True,'white'), (20,20)  )
        


        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)
        

    pygame.quit()


asyncio.run( main() )
