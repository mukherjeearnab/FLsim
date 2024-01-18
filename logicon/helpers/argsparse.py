'''
Args Parser Module
'''
import argparse
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()

# extra args
parser.add_argument("-d", "--debug", action="store_true")


parsed_args = parser.parse_args()

args = dict()


args['debug'] = parsed_args.debug
