from .eval_js import eval_js
from . import launch
from . import scripts
from . import emojis


from os.path import isfile, exists
from os import mkdir

if not exists(path='sessions'):
    mkdir(path='sessions')

if not isfile(path='config/proxies.txt'):
    with open('config/proxies.txt', 'w') as file:
        file.write('')
