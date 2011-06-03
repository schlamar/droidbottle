import re
import sqlite3
from collections import namedtuple
from subprocess import Popen, PIPE

import android
import bottle

bottle.debug(True)

Message = namedtuple('Message', ['id', 'address', 'body', 'date', 'sent'])

class Cache(object):
    '''Cache for data using a sqlite in memory database.'''
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
        cur.execute('''select id, address, body, sent
        from message where address=?''', (address,))
        for m_id, address, body, sent in cur:
            yield Message(m_id, address, body, None, sent)


class App(bottle.Bottle):
    def __init__(self):
        bottle.Bottle.__init__(self)
        self.droid = android.Android()
        self.cache = Cache(self.droid)


    def print_ip(self):
        out,_ = Popen('netcfg', stdout=PIPE).communicate()
        ip_pat = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        pattern = re.compile('tiwlan0\s+UP\s+(%s)' % ip_pat)
        match = pattern.search(out)
        ip = match.group(1) if match is not None else ''
        self.droid.notify('droidbottle', 'Running on "%s:8080"' % ip)


app = App()


@app.route('/sms')
def sms_groups():
    ret = '<ul>\n'
    for address in app.cache.get_message_groups():
        ret += '<li><a href="/sms/%s">%s</a></li>' % ((address,) * 2)
    ret += '</ul>'
    return ret


@app.route('/sms/:address')
def sms_group(address):
    ret = '<ul>\n'
    for msg in app.cache.get_message_group(address):
        adr = 'Me' if msg.sent else msg.address
        ret += '<li>%s: %s</li>' % (adr, msg.body)
    ret += '</ul>'
    return ret


@app.route('/')
def index():
    bottle.redirect('/sms')


if __name__ == '__main__':
    try:
        app.print_ip()
    except OSError:
        pass
    bottle.run(app, host='', port=8080)
