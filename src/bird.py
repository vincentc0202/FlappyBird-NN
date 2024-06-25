import pygame
import random
import os

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0 
        self.vel = 0
        self.height = self.y
        self.imgCount = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5        #negative velocity because (0,0) is top left of screen
        self.tickCount = 0
        self.height = self.y

    def move(self):
        self.tickCount += 1

        distance = self.vel * self.tickCount + 1.5 * self.tickCount ** 2    #creates a downwards parabola
        if distance >= 16:
            distance = 16
        if distance < 0:
            distance -= 2

        self.y = self.y + distance
        
        if distance < 0 or self.y < self.height + 50:                       #moving upwards or still above our initial height
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:                                                               #moving downwards
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.imgCount += 1
        # imgs go from 0 -> 1 -> 2 -> 1 -> 0 to show flapping 
        if self.imgCount < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.imgCount < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.imgCount < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.imgCount < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.imgCount < self.ANIMATION_TIME*5:
            self.img = self.IMGS[0]
            self.imgCount = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.imgCount = self.ANIMATION_TIME*2
        
        #to rotate the image around its center, not its top left corner
        rotatedImage = pygame.transform.rotate(self.img, self.tilt)
        newRect = rotatedImage.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotatedImage, newRect.topleft)
    
    def getMask(self):
        return pygame.mask.from_surface(self.img)