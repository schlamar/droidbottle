import re
from subprocess import Popen, PIPE

import bottle
from bottle import route, run

bottle.debug(True)

def get_ip():
    out,_ = Popen('netcfg', stdout=PIPE).communicate()
    pattern = re.compile('tiwlan0\s+UP\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    match = pattern.search(out)
    if match is not None:
        return match.group(1)

@route('/')
@route('/:name')
def index(name='World'):
    return '<b>Hello %s!</b>' % name

if __name__ == '__main__':
    print get_ip()
    run(host='', port=8080)
