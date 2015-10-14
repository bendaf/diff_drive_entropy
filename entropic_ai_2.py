# Basic game physics: ball collisions, gravity, drag, springs,... http://www.petercollingridge.co.uk/book/export/html/6
# Top down box collide: F=m*a
# Angular momentum and rotation?

"""
class Path:
    self.raced_distance
    self.end_point = (x, y)

"""
import pygame
import sys
from PIL import Image
import random
import math

pygame.init()
clock = pygame.time.Clock()
rad = math.pi/180

# Load map with PIL
img = Image.open('track_3_2.bmp')
track = img.load()


# Load map with matplotlib:
#img = mpimg.imread("track_3_2.bmp")
#track = img.tolist()
#print("track infos...")
#print(type(track))
#print(len(track), len(track[0]))

(width, height) = (640, 480)
#(width, height) = (len(track[0]), len(track))

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Entropic AI')

background_image = pygame.image.load("track_3_2.bmp").convert()

background_pos = [0, 0]


def is_free(x, y):
    return track[x, y] == (255, 255, 255)


def draw_pixel(surface, r, g, b, x, y):
    surface.fill((r, g, b), ((x, y), (2, 2)))


class Agent:
    def __init__(self, pos=(0, 0), size=5, speed=0.0, orientation=0):
        self.p_x, self.p_y = pos
        self.size = size
        self.speed = speed
        self.orientation = orientation

        self.number_of_paths = 40
        self.time_horizon = 20
        self.look_angle = 10

    def in_bounds(self):
        return 0 <= self.p_x <= width and 0 <= self.p_y <= height

    def move(self):
        self.p_x += math.cos(self.orientation) * self.speed
        self.p_y += math.sin(self.orientation) * self.speed

    def draw(self):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.p_x), int(self.p_y)), self.size, 1)
        #pygame.draw.rect(screen, (255, 0, 0), (self.p_x-1, self.p_y-1, 2, 2))
        pygame.draw.aaline(screen, (255, 0, 0), (int(self.p_x), int(self.p_y)),
                           (int(self.p_x+8*math.cos(self.orientation)), int(self.p_y+8*math.sin(self.orientation))))

    def sensor(self):
        

    def future_states(self):
        angle_decision_list = list(range(-self.look_angle, self.look_angle+1))
        final_positions = [set(), set()]
        final_speed = 0

        leftClone = Agent((self.p_x, self.p_y), self.size, self.speed, self.orientation)
        rightClone = Agent((self.p_x, self.p_y), self.size, self.speed, self.orientation)

        speeds = [self.speed-0.2, self.speed, self.speed+0.2]
        if self.speed == 3.0:
            speeds = [self.speed-0.2, self.speed]
        elif self.speed == 0.0:
            speeds = [self.speed, self.speed+0.2]

        for speed in speeds:
            futures = (set(), set())
            for i in range(self.number_of_paths):
                leftClone.p_x = self.p_x
                leftClone.p_y = self.p_y
                leftClone.orientation = self.orientation+self.look_angle*rad
                leftClone.speed = speed
                leftClone.move()
                rightClone.p_x = self.p_x
                rightClone.p_y = self.p_y
                rightClone.orientation = self.orientation-self.look_angle*rad
                rightClone.speed = speed
                rightClone.move()
                for dt in range(self.time_horizon):
                    omega = random.choice(angle_decision_list)
                    leftClone.orientation += omega*rad
                    leftClone.move()
                    if not is_free(int(leftClone.p_x), int(leftClone.p_y)):
                        break
                futures[0].add((int(round(leftClone.p_x)), int(round(leftClone.p_y))))
                for dt in range(self.time_horizon):
                    omega = random.choice(angle_decision_list)
                    rightClone.orientation += omega*rad
                    rightClone.move()
                    if not is_free(int(rightClone.p_x), int(rightClone.p_y)):
                        break
                futures[1].add((int(round(rightClone.p_x)), int(round(rightClone.p_y))))
            if len(final_positions[0])+len(final_positions[1]) < len(futures[0])+len(futures[1]):
                final_positions = (futures[0], futures[1])
                final_speed = max(min(speed, 3.0), 0.0)  # normalize speed
        return final_positions, final_speed

    def simulate(self):
        fut, s = self.future_states()
        d1 = len(fut[0])
        d2 = len(fut[1])
        n = d1 + d2
        #decision = self.look_angle*(d1/(d1+d2)) + (-self.look_angle)*(d2/(d1+d2))
        decision = self.look_angle*math.log(d1/n)-self.look_angle*math.log(d2/n)

        #print(d1, d2)
        #self.angle += int(round(decision))*rad
        self.orientation += decision*rad*3
        self.speed = s
        #print(self.angle)
        return list(fut[0]) + list(fut[1])


my_little_robot = Agent((187, 334), 7)
running = True
paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                sys.exit()
            if event.key == pygame.K_p:
                paused = True


        if event.type == pygame.MOUSEBUTTONDOWN:
            my_little_robot.p_x, my_little_robot.p_y = pygame.mouse.get_pos()
            my_little_robot.speed = 0

    screen.blit(background_image, background_pos)
    if not paused:
        future_points = my_little_robot.simulate()
        my_little_robot.move()
        print("velocity: ", my_little_robot.speed)
        for p in future_points:
            draw_pixel(screen, 0, 0, 255, *p)
    my_little_robot.draw()
    #pygame.draw.lines(screen, (0, 0, 255), False, future_points, 1)


    if not my_little_robot.in_bounds():
        running = False

    # Rect: https://www.pygame.org/docs/ref/rect.html
    #pygame.draw.rect(screen, (255, 255, 255), (10, 10, 20, 10), 1)

    pygame.display.flip()
    #msElapsed = clock.tick(50)
    # Fixed update for physics, time.deltaTime?
    # http://gafferongames.com/game-physics/fix-your-timestep/


pygame.quit()
