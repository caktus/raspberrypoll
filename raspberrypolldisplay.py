#!/usr/bin/env python
from __future__ import division

import sys
import os
import random
import time

import pygame


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
MAX_BAR_HEIGHT = SCREEN_HEIGHT - 100 - 50
FONT_FILE = os.path.join(os.path.dirname(__file__), '8bitwonder.ttf')


class Screen(object):

    width = SCREEN_WIDTH
    height = SCREEN_HEIGHT
    background_color = pygame.color.THECOLORS['black']

    def __init__(self):
        self.objects = []
        # Initialize pygame and create the display window
        pygame.init()
        pygame.display.set_caption("Raspberry Pi Poll Application")
        self.surface = pygame.display.set_mode((self.width, self.height))
        # Setup background
        self.background = pygame.Surface(self.surface.get_size()).convert()
        self.background.fill(self.background_color)

    def add(self, obj):
        self.objects.append(obj)

    def draw(self):
        self.surface.blit(self.background, (0, 0))
        for obj in self.objects:
            obj.draw(self.surface)
        pygame.display.flip()


class Bar(object):

    label_color = pygame.color.THECOLORS['white']

    def __init__(self, poll_display, label, (x, y), height, color=pygame.color.THECOLORS['white']):
        self.color = color
        self.poll_display = poll_display
        self.label = label
        self.x = x
        self.y = y
        self.height = height
        self.font = pygame.font.Font(FONT_FILE, 16)

    @property
    def get_bar_height(self):
        percent = self.height / (self.poll_display.highest_value or 1)
        return percent * MAX_BAR_HEIGHT

    def draw_label(self, to):
        text = self.font.render(self.label, True, self.label_color)
        textpos = text.get_rect()
        textpos.move_ip(self.x, self.y + 30)
        to.blit(text, textpos)

    def draw_bar(self, to):
        rect = pygame.Rect(self.x, self.y - self.get_bar_height, 100, self.get_bar_height)
        pygame.draw.rect(to, self.color, rect)

    def draw_value(self, to):
        text = self.font.render(str(self.height), True, self.label_color)
        textpos = text.get_rect()
        textpos.move_ip(self.x, self.y - self.get_bar_height - 30)
        to.blit(text, textpos)

    def draw(self, to):
        self.draw_bar(to)
        self.draw_label(to)
        self.draw_value(to)


class PollDisplay(object):

    BAR_COLORS = (
        pygame.color.THECOLORS['blue'],
        pygame.color.THECOLORS['red'],
        pygame.color.THECOLORS['green'],
        pygame.color.THECOLORS['yellow'],
        pygame.color.THECOLORS['purple'],
    )

    def __init__(self, datasource):
        self.screen = Screen()
        self.font = pygame.font.Font(FONT_FILE, 24)
        self.datasource = datasource
        self.poll_id = datasource.get_next_poll()

        self.bars = []
        choices = datasource.get_choices()

        graph_width = SCREEN_WIDTH - 50 - 50
        num_choices = len(choices)
        gap = (graph_width - (num_choices * 100)) / ((num_choices - 1) or 1)
        for i, label in choices:
            bar = Bar(self, label, (50 + (i * (100 + gap)), 400), 0, color=self.BAR_COLORS[i])
            self.bars.append(bar)
            self.screen.add(bar)

        self.screen.add(self)

    def next_poll(self):
        self.poll_id = self.datasource.get_next_poll()

    def show_poll(self):
        data = self.datasource.get_poll_results(self.poll_id)
        self.highest_value = max(data)
        for i, n in enumerate(data):
            self.bars[i].height = n
        self.screen.draw()

    def draw(self, to):
        text = self.font.render(self.datasource.get_poll_name(self.poll_id), True, pygame.color.THECOLORS['white'])
        textpos = text.get_rect()
        textpos.move_ip((640 / 2) - (textpos.width / 2), 0)
        to.blit(text, textpos)


class RandomPollDataSource(object):
    def __init__(self, dbpath, choices=None):
        self.dbpath = dbpath
        if choices is None:
            choices = random.choice(range(2, 6))
        self.bars = [0 for i in xrange(choices)]

    def get_choices(self):
        return [(i, str(i)) for i, bar in enumerate(self.bars)]

    def get_next_poll(self):
        return 1

    def get_poll_results(self, poll_id):
        i = random.choice(range(len(self.bars)))
        self.bars[i] += int(random.random() * 10)
        return self.bars[:]

    def get_poll_name(self, poll_id):
        return "Poll %d" % (poll_id,)


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
