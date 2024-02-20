'''
The Logging Module
'''
import logging
import datetime
from helpers.argsparse import args


class ColoredFormatter(logging.Formatter):
    '''
    Enables Colored Logs
    '''

    def __init__(self, debug=False):
        super().__init__()

        self.grey = "\x1b[0;37m"
        self.green = "\x1b[1;32m"
        self.yellow = "\x1b[33;20m"
        self.red = "\x1b[31;20m"
        self.bold_red = "\x1b[31;1m"
        self.reset = "\x1b[0m"

        if debug:
            self.log_format = '%(asctime)s [%(levelname)s] - [%(pathname)s > %(funcName)s() > %(lineno)d]\n[MSG] %(message)s'
            self.datefmt = '%d-%b-%y %H:%M:%S'
        else:
            self.log_format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
            self.datefmt = '%H:%M:%S'

        self.FORMATS = {
            logging.DEBUG: self.grey + self.log_format + self.reset,
            logging.INFO: self.grey + self.log_format + self.reset,
            25: self.green + self.log_format + self.reset,  # success
            logging.WARNING: self.yellow + self.log_format + self.reset,
            logging.ERROR: self.red + self.log_format + self.reset,
            logging.CRITICAL: self.bold_red + self.log_format + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# set success level
logging.SUCCESS = 25  # between WARNING and INFO
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
setattr(logger, 'success', lambda message, *
        args: logger._log(logging.SUCCESS, message, args))

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter()

# add formatter to ch
ch.setFormatter(ColoredFormatter(debug=args['debug']))

# add ch to logger
logger.addHandler(ch)

# add file handler
fh = logging.FileHandler(
    r'./logs/{date:%Y-%m-%d_%H:%M:%S}.log'.format(date=datetime.datetime.now()), mode='w')
fh.setFormatter(logging.Formatter())
logger.addHandler(fh)

logger.propagate = False
