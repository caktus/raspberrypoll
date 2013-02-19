#!/usr/bin/env python

import sys
import datetime
import sqlite3
import random
import time

db = sqlite3.connect(sys.argv[1])
cur = db.cursor()
poll_index = -1

if len(sys.argv) > 2:
    poll_name = sys.argv[2]
    slug = poll_name.replace(' ', '-').lower()
    option_labels = sys.argv[3:]

    cur.execute("insert into textpoll_poll (text, slug, active) values (?, ?, 1)", (poll_name, slug))
    poll_id = cur.lastrowid
    for label in option_labels:
        cur.execute("insert into textpoll_option (poll_id, text) values (?, ?)", (poll_id, label))
    db.commit()

while True:
    cur.execute("select id from textpoll_poll order by id")
    poll_ids = cur.fetchall()
    poll_index += 1
    poll_id = poll_ids[poll_index % len(poll_ids)][0]

    cur.execute("select id from textpoll_option where poll_id = ?", (poll_id,))
    option_ids = [r[0] for r in cur.fetchall()]

    option_id = random.choice(option_ids)
    cur.execute("insert into rapidsms_connection (backend_id, identity) values (?, ?)", (1, random.random()))
    cur.execute("insert into textpoll_vote (poll_id, connection_id, option_id, text, date) values (?, ?, ?, '', ?)", (poll_id, cur.lastrowid, option_id, datetime.datetime.now()))
    db.commit()

    print poll_id, option_id
    time.sleep(1)
