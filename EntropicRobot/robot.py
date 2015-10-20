import pygame
import math
import random
from vector_math import Vector2


class Robot:
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
        step_per_degree = 10
        sensor_angle = 20
        n = step_per_degree * sensor_angle
        distances = list()
        for i in range(n):
            degree = i / step_per_degree - sensor_angle/2 + self.angle

            # distances.append(self.get_distance(degree))
            dist = self.get_distance(degree)
            distances.append(dist)
            # print('distance in ', int(round(degree * 10)) / 10, ' is ', int(round(dist)))
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
        if 0 < degree % 360 <= 90:
            current_x = 0.1
            current_y = 0.1
        elif 90 < degree % 360 <= 180:
            current_x = -0.1
            current_y = 0.1
        elif 180 < degree % 360 <= 270:
            current_x = -0.1
            current_y = -0.1
        else:
            current_x = 0.1
            current_y = -0.1

        while self.environment.is_free(int(self.pos.x + current_x), int(self.pos.y + current_y)):
            real_y = current_x * math.tan(math.radians(degree))
            try:
                real_x = current_y / math.tan(math.radians(degree))
            except ZeroDivisionError:
                real_x = 0

            if abs(real_x) > abs(real_y):
                if real_x > 0:
                    current_x += 1
                else:
                    current_x -= 1
            else:
                if real_y > 0:
                    current_y += 1
                else:
                    current_y -= 1

        self.environment.draw_pixel(0, 255, 0, int(self.pos.x + current_x), int(self.pos.y + current_y))
        return math.hypot(current_x, current_y)

    def calculate_different_macrostates(self, option, speed):
        macrostates = set()
        angle_options = list(range(-self.lookAngle, self.lookAngle+1))
        curr_pos = Vector2(self.pos.x, self.pos.y)  # copy.copy(self.pos) # import copy
        curr_angle = self.angle

        def simulate_step(angle, s):
            nonlocal curr_angle
            curr_angle += angle
            nonlocal curr_pos
            curr_pos.x += math.cos(math.radians(curr_angle)) * s
            curr_pos.y += math.sin(math.radians(curr_angle)) * s

        simulate_step(option, speed)
        init_pos = Vector2(curr_pos.x, curr_pos.y)
        init_angle = curr_angle
        for i in range(self.numberOfPaths):
            curr_pos = Vector2(init_pos.x, init_pos.y)
            curr_angle = init_angle
            for dt in range(self.timeHorizon):
                omega = random.choice(angle_options)  # random decision
                simulate_step(omega, speed)
                if not self.environment.is_free(*curr_pos.as_int()):
                    break
            macrostates.add(curr_pos.as_int())

        return macrostates

    def simulate(self):
        option1 = self.lookAngle  # right
        option2 = -self.lookAngle  # left
        final_speed = 0
        highest_entropy = [set(), set()]

        if self.speed <= 0.2:
            self.lookAngle = 100
        else:
            self.lookAngle = 10

        #speed_options = list()  # list of different speed options
        if self.speed == self.maxSpeed:
            speed_options = [self.speed-0.2, self.speed]
        elif self.speed == self.minSpeed:
            speed_options = [self.speed, self.speed+0.2]
        else:
            speed_options = [self.speed-0.2, self.speed, self.speed+0.2]

        for speed in speed_options:
            different_futures_opt1 = self.calculate_different_macrostates(option1, speed)
            different_futures_opt2 = self.calculate_different_macrostates(option2, speed)
            if len(highest_entropy[0])+len(highest_entropy[1]) < len(different_futures_opt1)+len(different_futures_opt2):
                highest_entropy = (different_futures_opt1, different_futures_opt2)
                final_speed = max(min(speed, self.maxSpeed), self.minSpeed)

        d1 = len(highest_entropy[0])
        d2 = len(highest_entropy[1])
        n = d1 + d2
        #decision = self.look_angle*(d1/(d1+d2)) + (-self.look_angle)*(d2/(d1+d2))
        decision = option1*math.log(d1/n)+option2*math.log(d2/n)

        #print(d1, d2)
        k = 2.5  # gain
        self.angle += decision * k
        self.speed = final_speed
        #print(self.angle)
        return list(highest_entropy[0]) + list(highest_entropy[1])

    def in_bounds(self):
        return 0 <= self.pos.x <= self.environment.width and 0 <= self.pos.y <= self.environment.height