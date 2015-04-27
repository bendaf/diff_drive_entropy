import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.patches import RegularPolygon
import matplotlib.image as mpimg

deg = np.pi / 180


class Agent:
    def __init__(self, position, size, angle=0):
        self.speed = 2.
        self.angle = angle  # rad
        self.size = size
        self.x, self.y = position
        self.color = "green"
        self.v_l = 2  # left wheel
        self.v_r = 2  # right wheel
        self.L = size * 2  # wheel distance
        self.R = size / 4  # wheel radius
        self.factor = 1.

    def move(self):
        self.x += np.cos(self.angle) * self.speed
        self.y += np.sin(self.angle) * self.speed
        self.v_l = (2 * self.speed - self.angle * self.L) / 2 * self.R
        self.v_r = (2 * self.speed + self.angle * self.L) / 2 * self.R
        # print("v_l = ", self.v_l, "v_r = ", self.v_r)

    def future_states(self):
        futures = (set(), set())
        N = 50
        T = 40
        init_turn = 5
        decision1 = Agent((self.x, self.y), self.size, self.angle + init_turn * deg)
        # decision1.move()
        decision2 = Agent((self.x, self.y), self.size, self.angle - init_turn * deg)
        #decision2.move()
        for i in range(N):
            decision1.x = self.x
            decision1.y = self.y
            decision1.angle = self.angle + init_turn * deg
            decision1.move()
            decision2.x = self.x
            decision2.y = self.y
            decision2.angle = self.angle - init_turn * deg
            decision2.move()
            for dt in range(T):
                d = np.random.random_integers(0, 10) - 5
                #print('random deg: ', d*deg)
                decision1.angle += d * deg
                decision1.move()
                #print(decision1.angle, round(decision1.x), round(decision1.y))
                if track[int(round(decision1.y))][int(round(decision1.x))] != [255., 255.,
                                                                               255.]:  # or int(round(decision1.x)) < 640 or int(round(decision1.y)) < 480:
                    break
            futures[0].add((int(round(decision1.x)), int(round(decision1.y))))
            for dt in range(T):
                d = np.random.random_integers(0, 10) - 5
                #print('random deg2: ', d*deg)
                decision2.angle += d * deg
                decision2.move()
                if track[int(round(decision2.y))][int(round(decision2.x))] != [255., 255.,
                                                                               255.]:  # or int(round(decision2.x)) < 640 or int(round(decision2.y)) < 480:
                    break
            futures[1].add((int(round(decision2.x)), int(round(decision2.y))))

        #print(futures)
        return futures

    def simulate(self):
        futures = self.future_states()
        self.sensor()
        d1 = len(futures[0])
        d2 = len(futures[1])
        decision = 5 * (d1 / (d1 + d2)) + (-5) * (d2 / (d1 + d2))
        # print(d1, d2)
        #self.angle += int(round(decision))*deg
        self.angle += decision * deg * 10 * self.factor
        #print(self.angle)


    def collission(self):
        # collision_points = []
        collision = False
        col_size = self.size
        for i in range(int(self.angle / deg) - 120, int(self.angle / deg) + 121, 30):
            x = self.x + np.cos(i * deg) * col_size
            y = self.y + np.sin(i * deg) * col_size
            if track[int(round(y))][int(round(x))] != [255., 255., 255.]:
                collision = True

                #collision_points.append((x, y))
        colfigure = plt.figure(2)
        #plt.axes(xlim=(0, 640), ylim=(0, 480), aspect='equal')
        #plt.plot([p[0] for p in collision_points], [p[1] for p in collision_points], 'o', ms=1)
        if collision:
            self.factor += 0.05
            print("Collision")
        else:
            self.factor = 1.

    def get_distance(self, degree):
        current_x = 1
        current_y = 0
        while track[int(round(self.y + current_y))][int(round(self.x + current_x))] != [0., 0., 0.]:
            real_x = current_y * math.tan(math.radians(degree))
            real_y = current_x * math.tan(math.radians(degree))
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
        return math.hypot(current_x, current_y)

    def sensor(self):
        n = 100
        distances = list()
        for i in range(n):
            degree = i / 10 - 5
            # distances.append(self.get_distance(degree))
            print('distance in ', int(round(degree*10))/10, ' is ', int(round(self.get_distance(degree))))
        return distances

# -------------------------------------------
# Set up figure and animation
pause = False


def onClick(event):
    global pause
    #print('pause: ', pause)
    agent.x = event.xdata
    agent.y = event.ydata
    pause ^= True


def press(event):
    global pause
    if event.key == 'x':
        pause ^= True


fig = plt.figure()

img = mpimg.imread('track_ps.bmp')
track = img.tolist()
#print(len(track), len(track[0]))  # 480, 640

#ax = plt.axes(xlim=(0, len(track[0])), ylim=(0, len(track)), aspect='equal')  # így lefejjel rajzolta ki a képet
ax = fig.add_subplot(111)
plt.imshow(img)

#print(track)
agent = Agent((187, 334), 6)

#square = RegularPolygon((100,120), 4, radius=10, orientation=0, color="blue")
square = RegularPolygon((agent.x, agent.y), 4, radius=agent.size, orientation=agent.angle, color=agent.color)
#print(type(square.xy))
ax.add_patch(square)


# initialization function: plot the background of each frame
def init():
    square.set_alpha(0)
    return [square]


# animation function.  This is called sequentially
def animate(i):
    if not pause:
        #print(i)
        square.set_alpha(1)
        agent.collission()
        agent.simulate()
        agent.move()
        square.xy = (agent.x, agent.y)
        square.orientation = np.pi / 4 + agent.angle
    return [square]


'''
from time import time
t0 = time()
animate(0)
t1 = time()
interval = (t1 - t0)
print('inteval: ', interval)
'''
fig.canvas.mpl_connect('button_press_event', onClick)
fig.canvas.mpl_connect('key_press_event', press)
# call the animator.  blit=True means only re-draw parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               interval=20, blit=True)
#anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
plt.show()
