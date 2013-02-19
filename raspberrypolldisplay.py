#!/usr/bin/env python
from __future__ import division

import sys
import os
import random
import time
import sqlite3
from datetime import datetime, timedelta

import pygame


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
MAX_BAR_HEIGHT = SCREEN_HEIGHT - 100 - 90
FONT_FILE = os.path.join(os.path.dirname(__file__), 'PressStart2P.ttf')
LOGO_FILE = os.path.join(os.path.dirname(__file__), 'caktus-logo.png')


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

    def clear(self):
        self.objects = []

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
        text = self.font.render(self.label, False, self.label_color)
        textpos = text.get_rect()
        textpos.move_ip(self.x, self.y + 30)
        to.blit(text, textpos)

    def draw_bar(self, to):
        rect = pygame.Rect(self.x, self.y - self.get_bar_height, 100, self.get_bar_height)
        pygame.draw.rect(to, self.color, rect)

    def draw_value(self, to):
        text = self.font.render(str(self.height), False, self.label_color)
        textpos = text.get_rect()
        textpos.move_ip(self.x, self.y - self.get_bar_height - 30)
        to.blit(text, textpos)

    def draw(self, to):
        self.draw_bar(to)
        self.draw_label(to)
        self.draw_value(to)


class Sprite(object):
    def __init__(self, image, rescale=1):
        self.rect = image.get_rect()
        if rescale > 1:
            width = self.rect.width
            height = self.rect.height
            image = pygame.transform.scale(image, (int(width / rescale), int(height / rescale)))
            image = pygame.transform.scale(image, (width, height))
        self.image = image
        self.width = self.rect.width
        self.height = self.rect.height

    def move_to(self, x, y):
        self.rect.move_ip(x, y)

    def draw(self, to):
        to.blit(self.image, self.rect)


class PollDisplay(object):

    BAR_COLORS = [
        pygame.color.THECOLORS['blue'],
        pygame.color.THECOLORS['red'],
        pygame.color.THECOLORS['green'],
        pygame.color.THECOLORS['yellow'],
        pygame.color.THECOLORS['purple'],
    ]

    def __init__(self, datasource):
        self.screen = Screen()
        self.font = pygame.font.Font(FONT_FILE, 20)
        self.logo = Sprite(pygame.image.load(LOGO_FILE), rescale=2)
        self.logo.move_to(self.screen.width/2 - self.logo.width/2, self.screen.height - self.logo.height)

        self.datasource = datasource
        self.change_at = datetime.now() + timedelta(seconds=30)
        self.next_poll()

    def setup_bars(self):
        self.screen.clear()
        self.bars = []
        choices = self.datasource.get_choices(self.poll_id)

        graph_width = SCREEN_WIDTH - 50 - 50
        num_choices = len(choices)
        gap = (graph_width - (num_choices * 100)) / ((num_choices - 1) or 1)
        for i, label in choices:
            bar = Bar(self, label, (50 + (i * (100 + gap)), 360), 0, color=self.BAR_COLORS[i])
            self.bars.append(bar)
            self.screen.add(bar)
        self.screen.add(self.logo)
        self.screen.add(self)

    def next_poll(self):
        self.poll_id = self.datasource.get_next_poll()
        random.shuffle(self.BAR_COLORS)
        self.setup_bars()

    def show_poll(self):
        if self.change_at <= datetime.now():
            self.change_at = datetime.now() + timedelta(seconds=30)
            self.next_poll()

        data = self.datasource.get_poll_results(self.poll_id)
        self.highest_value = max(data)
        for i, n in enumerate(data):
            self.bars[i].height = n

        
        self.screen.draw()

    def draw(self, to):
        text = self.font.render(self.datasource.get_poll_name(self.poll_id), False, pygame.color.THECOLORS['white'])
        textpos = text.get_rect()
        textpos.move_ip((640 / 2) - (textpos.width / 2), 5)
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


class SqlitePollDataSource(object):
    def __init__(self, dbpath, choices=None):
        self.dbpath = dbpath
        self.db = sqlite3.connect(dbpath)
        self.cur = self.db.cursor()
        self.poll_index = 0

    def get_choices(self, poll_id):
        self.cur.execute("select text from textpoll_option where poll_id = ? order by id", (poll_id,))
        return [(i, r[0]) for (i, r) in enumerate(self.cur.fetchall())]

    def get_next_poll(self):
        self.cur.execute("select id from textpoll_poll order by id")
        ids = [r[0] for r in self.cur.fetchall()]
        self.poll_index += 1
        return ids[self.poll_index % len(ids)]

    def get_poll_results(self, poll_id):
        self.cur.execute("select id from textpoll_option where poll_id = ? order by id", (poll_id,))
        options = [r[0] for r in self.cur.fetchall()]
        scores = [0 for _ in options]
        for i, option_id in enumerate(options):
            self.cur.execute("select count(id) from textpoll_vote where poll_id = ? and option_id = ?", (poll_id, option_id))
            scores[i] = self.cur.fetchone()[0]

        return scores

    def get_poll_name(self, poll_id):
        self.cur.execute("select text from textpoll_poll where id = ?", (poll_id,))
        return self.cur.fetchone()[0]


def main(argv):

    source_path = argv[1]
    if source_path == ":random:":
        PollDataSource = RandomPollDataSource
    else:
        PollDataSource = SqlitePollDataSource

    datasource = PollDataSource(source_path)

    app = PollDisplay(datasource)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        time.sleep(0.5)
        app.show_poll()

if __name__ == "__main__":
    main(sys.argv)
