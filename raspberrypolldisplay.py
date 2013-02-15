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

    def __init__(self, label, (x, y), height):
        self.label = label
        self.x = x
        self.y = y
        self.height = height

    def draw(self, to):
        rect = pygame.Rect(self.x, self.y - self.height, 100, self.height)
        pygame.draw.rect(to, (255, 255, 255), rect)


class PollDisplay(object):
    def __init__(self, datasource):
        self.screen = Screen()
        self.datasource = datasource
        self.poll_id = datasource.get_next_poll()

        self.bars = []
        choices = datasource.get_choices()

        graph_width = 640 - 50 - 50
        num_choices = len(choices)
        gap = (graph_width - (num_choices * 100)) / ((num_choices - 1) or 1)
        for i, label in choices:
            bar = Bar(label, (50 + (i * (100 + gap)), 400), 0)
            self.bars.append(bar)
            self.screen.add(bar)

    def next_poll(self):
        self.poll_id = self.datasource.get_next_poll()

    def show_poll(self):
        data = self.datasource.get_poll_results(self.poll_id)
        for i, n in enumerate(data):
            self.bars[i].height = n
        self.screen.draw()


class RandomPollDataSource(object):
    def __init__(self, dbpath, choices=None):
        self.dbpath = dbpath
        if choices is None:
            choices = random.choice(range(1, 6))
        self.bars = [0 for i in xrange(choices)]

    def get_choices(self):
        return [(i, str(i)) for i, bar in enumerate(self.bars)]

    def get_next_poll(self):
        return 1

    def get_poll_results(self, poll_id):
        i = random.choice(range(len(self.bars)))
        self.bars[i] += int(random.random() * 10)
        return self.bars[:]


PollDataSource = RandomPollDataSource


def main(argv):

    datasource = PollDataSource(argv[-1])

    app = PollDisplay(datasource)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        time.sleep(0.5)
        app.show_poll()

if __name__ == "__main__":
    main(sys.argv)
