#!/usr/bin/env python

import os, sys
import random
import time

import pygame


class Screen(object):

    width = 640
    height = 480

    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((self.width, self.height))

        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def draw(self):
        for obj in self.objects:
            obj.draw(self.surface)
        pygame.display.flip()


class Bar(object):

    def __init__(self, (x, y), height):
        self.x = x
        self.y = y
        self.height = height

    def draw(self, to):
        rect = pygame.Rect(self.x, self.y - self.height, 100, self.height)
        pygame.draw.rect(to, (255, 255, 255), rect)


class PollDisplay(object):
    def __init__(self):
        self.screen = Screen()
        self.bars = []
        for i in xrange(4):
            bar = Bar((48 + (i * 148), 400), 0)
            self.bars.append(bar)
            self.screen.add(bar)

    def run(self):
        i = random.choice(range(4))
        bar = self.bars[i]
        bar.height += int(random.random() * 10)

        self.screen.draw()


def main():

    app = PollDisplay()

    while True:
        time.sleep(0.5)
        app.run()
    
if __name__ == "__main__":
    main()
