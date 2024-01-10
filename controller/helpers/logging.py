'''
The Logging Module
'''
import logging
import datetime

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s [%(levelname)s] - [%(pathname)s > %(funcName)s() > %(lineno)d]\n[MSG] %(message)s',
                              datefmt='%d-%b-%y %H:%M:%S')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# add file handler
fh = logging.FileHandler(
    r'./logs/{date:%Y-%m-%d_%H:%M:%S}.log'.format(date=datetime.datetime.now()), mode='w')
fh.setFormatter(formatter)
logger.addHandler(fh)


# def log_debug(msg: str) -> None:
#     '''
#     Log DEBUG message
#     '''
#     logger.debug(msg)

# def log_info(msg: str) -> None:
#     '''
#     Log INFO message
#     '''
#     logger.info(msg)

# def log_warning(msg: str) -> None:
#     '''
#     Log WARNING message
#     '''
#     logger.warning(msg)

# def log_error(msg: str) -> None:
#     '''
#     Log ERROR message
#     '''
#     logger.error(msg)

# def log_critical(msg: str) -> None:
#     '''
#     Log CRITICAL message
#     '''
#     logger.critical(msg)
