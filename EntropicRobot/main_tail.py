import pygame
import sys
from PIL import Image  # Python Imaging Library
from robot import Robot
from robot_goal import Robot as GRobot

pygame.init()

# load map with PIL
image_filename = "labirinth.bmp"


class Environment:
    def __init__(self):
        img = Image.open(image_filename)
        self.track = img.load()  # for pixel information
        self.width, self.height = img.size

    def get_size(self):
        return self.width, self.height

    def is_free(self, x, y):
        return self.track[x, y] == (255, 255, 255)

    def draw_pixel(self, r, g, b, x, y):
        global screen
        draw_pixel(screen, r, g, b, x, y)


def draw_pixel(surface, r, g, b, x, y):
        surface.fill((r, g, b), ((x, y), (2, 2)))

def robot_list_step():
    for r in robot_list:
        future_positions = r.simulate()
        r.move()
        try:
            for p in future_positions:
                draw_pixel(screen, 0, 0, 255, *p)
        except TypeError:
            pass

def robot_list_draw():
    for r in robot_list:
        r.draw(screen)
        if not r.in_bounds():
            global running
            running = False

environment = Environment()

#  Create screen
screen = pygame.display.set_mode((environment.get_size()))
pygame.display.set_caption('Entropic AI')
background = pygame.image.load(image_filename).convert()  # for display
# velocity_font = pygame.font.Font(None, 30)
robot_list = list()

robot_list.append(Robot(environment, environment.width/2, environment.height/2, 7))
robot_list.append(GRobot(environment, environment.width/2, environment.height/2, 7, goal=robot_list[0].pos, color=(0, 51, 102)))
walked_path = list()

clock = pygame.time.Clock()  # to measure fps
running = True
paused = False
draw_walked_path = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                sys.exit()
            elif event.key == pygame.K_p:
                paused ^= True
            elif event.key == pygame.K_f:
                draw_walked_path ^= True
            elif event.key == pygame.K_w:
                robot_list[0].timeHorizon += 5
                print("time horizon = ", robot_list[0].timeHorizon)
            elif event.key == pygame.K_s:
                robot_list[0].timeHorizon -= 5
                print("time horizon = ", robot_list[0].timeHorizon)
            elif event.key == pygame.K_d:
                robot_list[0].numberOfPaths += 5
                print("number of paths = ", robot_list[0].numberOfPaths)
            elif event.key == pygame.K_a:
                robot_list[0].numberOfPaths -= 5
                print("number of paths = ", robot_list[0].numberOfPaths)
            elif event.key == pygame.K_x:
                robot_list[0].maxSpeed += 1.0
                print("max speed = ", robot_list[0].maxSpeed)
            elif event.key == pygame.K_z:
                robot_list[0].maxSpeed -= 1.0
                print("max speed = ", robot_list[0].maxSpeed)

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())
            robot_list[0].pos.x, robot_list[0].pos.y = pygame.mouse.get_pos()
            robot_list[0].speed = 0
            robot_list[1].pos.x, robot_list[1].pos.y = pygame.mouse.get_pos()
            robot_list[1].speed = 0
            walked_path.clear()

    # screen.blit(background, [0, 0])  # redraw clean background
    # Update:
    if not paused:
        screen.blit(background, [0, 0])  # redraw clean background
        #robot_list_step()
        future_positions = robot_list[0].simulate()
        robot_list[0].move()
        for p in future_positions:
            draw_pixel(screen, 0, 0, 255, *p)

        robot_list[1].goal = robot_list[0].pos
        future_positions = robot_list[1].simulate()
        robot_list[1].move()
        robot_list[1].draw_futures(screen, future_positions)
        # paused = True

    robot_list_draw()
    #text = velocity_font.render("v = "+str(myRobot.speed), 1, (255, 0, 0))
    #screen.blit(text, (0, 0))

    if len(walked_path) > 1 and draw_walked_path:
        pygame.draw.lines(screen, (0, 255, 0), False, walked_path, 1)

    pygame.display.flip()
    #pygame.time.wait(30)  # to limit refresh rate
    """
    clock.tick()
    print("fps: ", clock.get_fps())
    """

pygame.quit()
