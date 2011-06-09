#!/usr/bin/env python
# coding: utf-8


import re
import sqlite3
from collections import namedtuple
from subprocess import Popen, PIPE

import android
import bottle
from bottle import view, route, post

bottle.debug(True)
bottle.TEMPLATE_PATH.append('/sdcard/sl4a/scripts/views')

Message = namedtuple('Message', ['body', 'sent'])

class Cache(object):
    '''Cache for data using a sqlite in-memory database.'''
    def __init__(self, droid):
        self.droid = droid
        self.conn = sqlite3.connect(':memory:')
        self._create_tables()
        self._init_sms_chache()


    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''create table message (
        id integer primary key, address text, body text,
        date integer, sent integer)''')
        self.conn.commit()


    def _init_sms_chache(self):
        for folder in ('inbox', 'sent'):
            for msg_obj in self.droid.smsGetMessages(False, folder).result:
                self._insert_message(msg_obj, folder == 'sent')


    def _insert_message(self, msg_obj, sent):
        cur = self.conn.cursor()
        cur.execute('insert into message values (?,?,?,?,?)',
                    (msg_obj['_id'], msg_obj['address'], msg_obj['body'],
                     msg_obj['date'], sent))
        self.conn.commit()


    def _update_sms_cache(self):
        cur = self.conn.cursor()
        for folder in ('inbox', 'sent'):
            sent = folder == 'sent'
            msgs = self.droid.smsGetMessageCount(False, folder).result
            cur.execute('select count(*) from message where sent=?',
                        (sent,))
            if msgs > cur.fetchone()[0]:
                new_ids = self.droid.smsGetMessageIds(False, folder).result
                old_ids = set()
                cur.execute('select id from message where sent=?', (sent,))
                for old_id, in cur:
                    old_ids.add(old_id)

                insert_ids = set(new_ids) - old_ids
                for new_id in insert_ids:
                    msg_obj = self.droid.smsGetMessageById(new_id).result
                    self._insert_message(msg_obj, sent)


    def get_message_groups(self):
        self._update_sms_cache()
        cur = self.conn.cursor()
        cur.execute('''select address from message group by address
        order by date desc''')
        for address, in cur:
            yield address

    def get_message_group(self, address):
        self._update_sms_cache()
        cur = self.conn.cursor()
        cur.execute('''select body, sent from message
        where address=?''', (address,))
        for body, sent in cur:
            yield Message(body, sent)


droid = android.Android()
cache = Cache(droid)


def print_ip():
    out,_ = Popen('netcfg', stdout=PIPE).communicate()
    ip_pat = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    pattern = re.compile('tiwlan0\s+UP\s+(%s)' % ip_pat)
    match = pattern.search(out)
    ip = match.group(1) if match is not None else ''
    droid.notify('droidbottle', 'Running on "%s:8080"' % ip)



@route('/sms')
@view('sms_threads')
def sms_threads():
    return dict(addresses=cache.get_message_groups())


@route('/sms/:address')
@view('sms_thread')
def sms_group(address):
    return dict(messages=cache.get_message_group(address),
                address=address,)


@route('/sms/:address/new')
@view('sms_form')
def sms_form(address):
    return dict(address=address)


@post('/sms/:address/new')
@view('sms_send')
def sms_send(address):
    act = 'android.intent.action.VIEW'
    atype = 'vnd.android-dir/mms-sms'
    extras = {'address': address,
              'sms_body': bottle.request.forms.get('body')}
    droid.startActivity(act, None, atype, extras)
    return dict(address=address)


@route('/')
def index():
    bottle.redirect('/sms')


if __name__ == '__main__':
    try:
        print_ip()
    except OSError:
        pass
    bottle.run(host='', port=8080)
