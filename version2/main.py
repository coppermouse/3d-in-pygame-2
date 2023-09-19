# ---------------------------------------- 
# file: main.py
# author: coppermouse
# ----------------------------------------

import asyncio
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
colors = np.array( colors )


async def main():
    global screen

    # declare camera variables
    camera_position = np.array([0.0,0.0])
    camera_angle = math.pi

    half_screen_size = np.array(screen.get_size()) // 2

    view_mode = 0
    low_res = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    view_mode = ( view_mode + 1 ) % 2
                if event.key == pygame.K_r:
                    camera_position = np.array([0.0,0.0])
                    camera_angle = math.pi
                if event.key == pygame.K_l:

                    low_res = ( low_res + 1 ) % 2

                    screen = pygame.display.set_mode(
                        (1920// ( 2 if low_res else 1), 1080//( 2 if low_res else 1)), 
                        pygame.SCALED | pygame.NOFRAME 
                    )
                    half_screen_size = np.array(screen.get_size()) // 2


        for k, delta in ( (pygame.K_w,-1), (pygame.K_s,1) ):
            if pygame.key.get_pressed()[k]:
                camera_position += np.array( [math.sin(camera_angle), math.cos(camera_angle)]  ) * 0.002 * delta


        for k, delta in ( (pygame.K_a,-1), (pygame.K_d,1) ):
            if pygame.key.get_pressed()[k]:
                camera_angle += delta * 0.05

    
        projected_polygons, filtered_colors = projection( 
            polygons, 
            colors, 
            camera_position, 
            camera_angle, 
            half_screen_size*(1,2), 
            half_screen_size, 
            near = (0.017, 0.45),
            view_mode = view_mode,
            fog_color = [ 64, 68, 70 ],
        )
    
        screen.fill( (64,68,70) )

        for polygon, color in zip( projected_polygons, filtered_colors ):
            pygame.draw.polygon( screen, color, polygon )


        f = clock.get_fps()
        screen.blit( font.render('fps: {0}'.format( round(f,2) ), True, 'white' ), (20,20)  )
        screen.blit( font.render("view mode: {0}. press 'm' to switch".format( view_mode  ), True, 'white' ), (20,40)  )
        screen.blit( font.render("low res: {0}. press 'l' to switch".format( low_res  ), True, 'white' ), (20,60)  )
        screen.blit( font.render("press 'r' to reset camera position", True, 'white' ), (20,80)  )

        pygame.display.flip()

        clock.tick(600)
        await asyncio.sleep(0)
        
    pygame.quit()

asyncio.run( main() )


