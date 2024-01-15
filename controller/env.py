import os
from dotenv import load_dotenv

# import environment variables
load_dotenv()

env = dict()

# load variables into object
env['LOGICON_URL'] = os.getenv('LOGICON_URL')
env['DATADIST_URL'] = os.getenv('DATADIST_URL')
env['DELAY'] = float(os.getenv('DELAY'))
# env['USE_CUDA'] = int(os.getenv('USE_CUDA'))
