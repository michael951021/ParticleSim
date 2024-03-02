import math

import pygame
import sys
from datetime import datetime

# Initialize pygame
pygame.init()

# Set up the screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Physics Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
gravity = 0.005
k = 10000              # 8.99*10e9

# Ball class
class Atom:
    def __init__(self, x, y, vx, vy, charge):
        # intrinsic
        self.radius = 20
        self.mass = 1  # in 'grams'
        self.velocitybuffer = [vx,vy]

        self.x = x
        self.y = y
        self.charge = charge
        if charge > 0:
            self.color = RED
        else:
            self.color = BLUE
        self.velocity = [vx, vy]
        self.ft = [0,math.atan2(vy,vx)] # Force vector in form [r,theta]

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Wall collision
        if self.y + self.radius >= height:
            self.y = height - self.radius
            self.velocitybuffer[1] = -self.velocity[1]
        elif self.y - self.radius <= 0:
            self.y = self.radius
            self.velocitybuffer[1] = -self.velocity[1]
        if self.x + self.radius >= width:
            self.x = width - self.radius
            self.velocitybuffer[0] = -self.velocity[0]
        elif self.x - self.radius <= 0:
            self.x = self.radius
            self.velocitybuffer[0] = -self.velocity[0]

    def isColliding(self, p2):
        if self.dist(p2) <= self.radius + p2.radius:
            return True

    def collision(self, p2):
        self.velocitybuffer[0] = (self.mass-p2.mass)*self.velocity[0]/(self.mass+p2.mass) + 2*p2.mass*p2.velocity[0]/(self.mass+p2.mass)
        self.velocitybuffer[1] = (self.mass - p2.mass) * self.velocity[1] / (self.mass + p2.mass) + 2 * p2.mass * p2.velocity[1] / (self.mass + p2.mass)


    def dist(self, p2):
        return math.sqrt((p2.x-self.x)**2 + (p2.y - self.y)**2)

    def updateForce(self, p):
        force_sum = [0,0] # fx fy
        for i in range(len(p)):
            if self != p[i] and self.dist(p[i]) != 0:  # might needa change to radius sum
                f = abs(k*self.charge*p[i].charge)/(self.dist(p[i])**2)
                t = math.atan2(p[i].y - self.y,p[i].x-self.x)
                # print("t: "+str(t))
                if self.charge * p[i].charge > 0:
                    t += math.pi
                force_sum[0] += f*math.cos(t)
                force_sum[1] += f*math.sin(t)
                # print(math.atan2(force_sum[1],force_sum[0]))
        self.ft = [math.sqrt(force_sum[0]**2+force_sum[1]**2),math.atan2(force_sum[1],force_sum[0])]
        #print(str(self.x) + " " + str(self.y) + " : " + str(self.ft[1]))

    def updateVelocities(self, dt):
        # print("cos: "+ str(math.cos(self.ft[1]) * dt / self.mass))
        # print(math.sin(self.ft[1]) * dt / self.mass)
        # print(self.ft[0] * math.cos(self.ft[1]))
        # print(dt)
        # print(self.ft[0] * math.cos(self.ft[1]) * dt)
        self.velocitybuffer[0] += self.ft[0] * math.cos(self.ft[1]) * dt / self.mass
        self.velocitybuffer[1] += self.ft[0] * math.sin(self.ft[1]) * dt / self.mass

    def drawVelocityVectors(self):
        pygame.draw.polygon(screen, BLACK, ((self.x-5,self.y),(self.x+self.velocity[0]*500,self.y+self.velocity[1]*500),(self.x+5,self.y)))

    def pushBuffer(self):
        self.velocity[0] = self.velocitybuffer[0]
        self.velocity[1] = self.velocitybuffer[1]

    def drawForceVectors(self):
        # print(self.ft[0])
        # print(self.ft[1])
        # print("self: " + str(self.x))
        # print(self.x+self.ft[0]*math.cos(self.ft[1])*5)
        # print(self.y+self.ft[0]*math.sin(self.ft[1])*5)
        pygame.draw.polygon(screen, GREEN, ((self.x-5,self.y),(int(self.x+self.ft[0]*math.cos(self.ft[1])*1e4),int(self.y+self.ft[0]*math.sin(self.ft[1])*1e4)),(self.x+5,self.y)))



# Create molecules
atoms = [Atom(50, 50, 0.01, -0.1, -1),Atom(width-50,height-50,-0.1,0.1, 1)]

# Main loop
dt = 0.001  # time (seconds) every loop
time_elapsed = 0;
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # Update forces
    for i in range(len(atoms)):
        atoms[i].updateForce(atoms)

    # Update velocities
    if dt != 0:
        for i in range(len(atoms)):
            atoms[i].updateVelocities(dt)

    # Show vectors <Force is green, Velocity is black>
    for i in range(len(atoms)):
        atoms[i].drawForceVectors()
        atoms[i].drawVelocityVectors()

    # Check for collision
    for i in range(len(atoms)):
        for j in range(i+1,len(atoms)):
            if atoms[i].isColliding(atoms[j]):
                print("a")
                atoms[i].collision(atoms[j])

    # Push velocities
    for i in range(len(atoms)):
        atoms[i].pushBuffer()

    # Update positions
    for i in range(len(atoms)):
        atoms[i].update()

    # Draw
    for i in range(len(atoms)):
        atoms[i].draw()

    pygame.display.flip()
    time_elapsed += dt;
