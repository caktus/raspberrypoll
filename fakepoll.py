#!/usr/bin/env python

import sys
import datetime
import sqlite3
import random
import time

db = sqlite3.connect(sys.argv[1])
cur = db.cursor()
cur.execute("select id from textpoll_poll order by id")
poll_id = cur.fetchall()[0][0]

cur.execute("select id from textpoll_option where poll_id = ?", (poll_id,))
option_ids = [r[0] for r in cur.fetchall()]

while True:
    time.sleep(1)
    option_id = random.choice(option_ids)
    cur.execute("insert into rapidsms_connection (backend_id, identity) values (?, ?)", (1, random.random()))
    cur.execute("insert into textpoll_vote (poll_id, connection_id, option_id, text, date) values (?, ?, ?, '', ?)", (poll_id, cur.lastrowid, option_id, datetime.datetime.now()))
    db.commit()
    print poll_id, option_id
