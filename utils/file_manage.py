from os.path import isfile, exists
from os import mkdir


if not exists(path='sessions'):
    mkdir(path='sessions')

if not isfile(path='settings.json'):
    with open('settings.json', 'w') as file:
        file.write('')

if not isfile(path='data/proxies.txt'):
    with open('data/proxies.txt', 'w') as file:
        file.write('')
