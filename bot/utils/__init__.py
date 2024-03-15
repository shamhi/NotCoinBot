from .eval_js import eval_js
from .launch import start_process, run_tasks
from . import scripts
from . import emojis


from os.path import isfile, exists
from os import mkdir

if not exists(path='sessions'):
    mkdir(path='sessions')

if not isfile(path='settings.json'):
    with open('settings.json', 'w') as file:
        file.write('')

if not isfile(path='bot/config/proxies.txt'):
    with open('bot/config/proxies.txt', 'w') as file:
        file.write('')
