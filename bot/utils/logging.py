from sys import stderr

from loguru import logger


logger.remove()

logger.add(sink=stderr,
           format='<white>{time:HH:mm:ss}</white>'
                  ' | <level>{level: <8}</level>'
                  ' | <cyan><b>{line}</b></cyan>'
                  ' - <white><b>{message}</b></white>')
logger.opt(colors=True)

logger.add(sink='logs.log', rotation='5 MB',
           format='<white>{time:HH:mm:ss}</white>'
                  ' | <level>{level: <8}</level>'
                  ' | <cyan>{line}</cyan>'
                  ' - <white>{message}</white>')
