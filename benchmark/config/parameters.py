import os

ARRAY_SIZE = 1000
ITERATIONS = int(os.environ.get('ITERATIONS', 10000))
DATA_SIZE = os.environ.get('DATA_SIZE', 'small')
TEST_RESULT_FOLDER = os.environ.get('TEST_RESULT_FOLDER', 'default')
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 1))
PROCESS_INDEX = int(os.environ.get('PROCESS_INDEX', 0))