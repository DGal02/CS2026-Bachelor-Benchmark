import json
import os
import numpy as np
from benchmark.config.parameters import ARRAY_SIZE

key_prefix = 'benchmark'
key_mix_prefix = 'mix'

def load_data(data_size):
    data_path = f'benchmark/data/{data_size}.json'
    with open(data_path) as f:
        raw = json.load(f)
    return np.array(raw)

def generate_key(index):
    return key_prefix + str(index)

def generate_key_mix(index):
    return key_mix_prefix + str(index)

def get_data(data, index):
    return data[index % ARRAY_SIZE]

def get_result_path(test_result_folder, max_workers, process_index, test_name):
    result_dir = f'testResult/{test_result_folder}/workers-{max_workers}'
    os.makedirs(result_dir, exist_ok=True)
    return f'{result_dir}/{test_name}-{process_index}.csv'