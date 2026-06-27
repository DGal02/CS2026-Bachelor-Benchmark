import json
import os
import numpy as np
from benchmark.config.parameters import ARRAY_SIZE, TEST_RESULT_FOLDER, DATA_SIZE, ITERATIONS, MAX_WORKERS, PROCESS_INDEX


key_prefix = 'benchmark'
key_mix_prefix = 'mix'

def load_data():
    data_path = f'benchmark/data/{DATA_SIZE}.json'
    with open(data_path) as f:
        raw = json.load(f)
    return np.array(raw)

def generate_key(index):
    return f'{key_prefix}-{PROCESS_INDEX}-{index}'

def generate_key_mix(index):
    return f'{key_mix_prefix}-{PROCESS_INDEX}-{index}'

def get_data(data, index):
    return data[index % ARRAY_SIZE]

def get_result_path(test_name):
    result_dir = f'testResult/{TEST_RESULT_FOLDER}/{DATA_SIZE}/{ITERATIONS}/workers-{MAX_WORKERS}'
    os.makedirs(result_dir, exist_ok=True)
    return f'{result_dir}/{test_name}-{PROCESS_INDEX}.csv'