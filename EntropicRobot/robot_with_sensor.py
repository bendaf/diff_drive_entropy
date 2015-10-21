import pygame
import math
import random
from vector_math import Vector2


class SRobot:
    def __init__(self, environment, x=0, y=0, size=5, speed=0.0, a=0):
        self.environment = environment
        self.pos = Vector2(x, y)
        self.size = size
        self.speed = speed
        self.angle = a  # deg !!!
        self.maxSpeed = 4.0
        self.minSpeed = 0.0

        # Entropic AI Parameters
        self.numberOfPaths = 70
        self.timeHorizon = 25
        self.lookAngle = 10
        self.step_per_degree = 2
        self.sensor_angle = 20

    def move(self):
        self.pos.x += math.cos(math.radians(self.angle)) * self.speed
        self.pos.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self, surface):
        angle_rad = math.radians(self.angle)
        pygame.draw.circle(surface, (255, 0, 0), self.pos.as_int(), self.size, 1)
        head = self.size+1
        pygame.draw.aaline(surface, (255, 0, 0), self.pos.as_int(),
                           (int(self.pos.x+head*math.cos(angle_rad)), int(self.pos.y+head*math.sin(angle_rad))))

    def sensor(self):
        n = self.step_per_degree * self.sensor_angle + 1
        distances = (list(), list())
        for i in range(n):
            degree = i / self.step_per_degree - self.sensor_angle/2

            # distances.append(self.get_distance(degree))
            dist = self.get_distance(self.angle + degree)
            distances[0].append(degree)
            distances[1].append(dist)
            # print('distance in ', round(degree, 1), ' is ', round(dist))
            # draw_pixel(screen, 0, 255, 0, self.p_x + int(math.cos(math.radians(degree)) * dist),
            #           int(self.p_y + math.sin(math.radians(degree)) * dist))
            #plt.plot([self.x + 0, self.x + math.cos(math.radians(degree)+self.angle) * dist],
            #         [self.y + 0, self.y + math.sin(math.radians(degree)+self.angle) * dist])
            #if degree == 0:
            #    print(int(self.p_x + math.sin(math.radians(degree) * dist)), " ",
            #          int(self.p_y + math.cos(math.radians(degree)) * dist))
        # print(round(degree,1))
        return distances

    def get_distance(self, degree):
        degree = round(degree, 1)

        current_x = math.cos(math.radians(degree))
        current_y = math.sin(math.radians(degree))

        # print(current_x," ",current_y)
        while self.environment.is_free(int(self.pos.x + current_x), int(self.pos.y + current_y)):
            real_y = current_x * math.tan(math.radians(degree))
            try:
                real_x = current_y / math.tan(math.radians(degree))
            except ZeroDivisionError:
                real_x = 100000

            if abs(real_x)-abs(current_x) > abs(real_y)-abs(current_y):
                if real_x > 0:
                    current_x += 1
                else:
                    current_x -= 1
            elif abs(real_x)-abs(current_x) < abs(real_y)-abs(current_y):
                if real_y > 0:
                    current_y += 1
                else:
                    current_y -= 1
            else:
                if real_y > 0:
                    current_y += 1
                else:
                    current_y -= 1
                if real_x > 0:
                    current_x += 1
                else:
                    current_x -= 1
            self.environment.draw_pixel(0, 255, 0, int(self.pos.x + current_x), int(self.pos.y + current_y))
        return math.hypot(int(current_x), int(current_y))

    def simulate(self):

        distances = self.sensor()
        decision = 0
        n = len(distances[1])
        avg = abs(sum(distances[1])/n)
        for i in range(n):
            decision += distances[0][i] * max(min(distances[1][i] / avg, 2), 0)

        decision = decision/n
        print("self.angle: ", self.angle, " dec: ", decision)
        self.angle += decision
        self.speed = max(min(avg/80, 3), 0.01)
        print("acg: ", avg)
        # return list(highest_entropy[0]) + list(highest_entropy[1])

    def in_bounds(self):
        return 0 <= self.pos.x <= self.environment.width and 0 <= self.pos.y <= self.environment.height