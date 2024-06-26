import os
from dotenv import load_dotenv

# import environment variables
load_dotenv()

env = dict()

# load variables into object
env['LOGICON_URL'] = os.getenv('LOGICON_URL')
env['P2PSTORE_URL'] = os.getenv('P2PSTORE_URL')
env['PERFLOG_URL'] = os.getenv('PERFLOG_URL')
env['DATADIST_URL'] = os.getenv('DATADIST_URL')
env['DELAY'] = float(os.getenv('DELAY'))
env['USE_CUDA'] = int(os.getenv('USE_CUDA'))
env['CLIENT_USE_CUDA'] = int(os.getenv('CLIENT_USE_CUDA'))
env['WORKER_USE_CUDA'] = int(os.getenv('WORKER_USE_CUDA'))
env['DISCOVERY_INTERVAL'] = int(os.getenv('DISCOVERY_INTERVAL'))
