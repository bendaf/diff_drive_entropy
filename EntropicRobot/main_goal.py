import pygame
import sys
from PIL import Image  # Python Imaging Library
from robot_goal import Robot
from vector_math import Vector2

pygame.init()

# load map with PIL
#image_filename = "track_new_3.bmp"
image_filename = "circle.bmp"


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


class Goal:
    def __init__(self, x=100, y=100, size=10):
        self.pos = Vector2(x, y)
        self.size = size

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.pos.x-self.size/2, self.pos.y-self.size/2, self.size, self.size))


def draw_pixel(surface, r, g, b, x, y):
        surface.fill((r, g, b), ((x, y), (2, 2)))

environment = Environment()

#  Create screen
width, height = environment.get_size()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Entropic AI')
background = pygame.image.load(image_filename).convert()  # for display
velocity_font = pygame.font.Font(None, 30)


goal = Goal(width-50, 350)
# myRobot = Robot(environment, 560, 90, 7)
myRobot = Robot(environment, width/2, height/2, 7, goal=goal.pos)
walked_path = list()

clock = pygame.time.Clock()
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
                myRobot.timeHorizon += 5
                print("time horizon = ", myRobot.timeHorizon)
            elif event.key == pygame.K_s:
                myRobot.timeHorizon -= 5
                print("time horizon = ", myRobot.timeHorizon)
            elif event.key == pygame.K_d:
                myRobot.numberOfPaths += 5
                print("number of paths = ", myRobot.numberOfPaths)
            elif event.key == pygame.K_a:
                myRobot.numberOfPaths -= 5
                print("number of paths = ", myRobot.numberOfPaths)
            elif event.key == pygame.K_x:
                myRobot.maxSpeed += 1.0
                print("max speed = ", myRobot.maxSpeed)
            elif event.key == pygame.K_z:
                myRobot.maxSpeed -= 1.0
                print("max speed = ", myRobot.maxSpeed)

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())
            #myRobot.pos.x, myRobot.pos.y = pygame.mouse.get_pos()
            #myRobot.speed = 0
            goal.pos.x, goal.pos.y = pygame.mouse.get_pos()
            myRobot.goal.x = goal.pos.x
            myRobot.goal.y = goal.pos.y
            walked_path.clear()

    screen.blit(background, [0, 0])  # redraw clean background
    # Update:
    goal.draw()
    if not paused:
        #myRobot.sensor()
        future_positions = myRobot.simulate()
        myRobot.move()
        walked_path.append(myRobot.pos.as_int())
        myRobot.draw_futures(screen, future_positions)

    # Draw
    myRobot.draw(screen)
    text = velocity_font.render("v = "+str(myRobot.speed), 1, (255, 0, 0))
    screen.blit(text, (0, 0))

    if len(walked_path) > 1 and draw_walked_path:
        pygame.draw.lines(screen, (0, 255, 0), False, walked_path, 1)

    if not myRobot.in_bounds():
        running = False

    pygame.display.flip()
    #pygame.time.wait(30)
    """
    clock.tick()
    print("fps: ", clock.get_fps())
    """

pygame.quit()