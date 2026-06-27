import json
import numpy as np
from benchmark.config.parameters import ARRAY_SIZE

# temporary solution, variables
iterations = 10000
data_size = 'small'
# end of variables


key_prefix = 'benchmark'

data_path = f'data/{data_size}.json'
with open(data_path) as f:
    _raw = json.load(f)
data = np.array(_raw)

def generate_key(index):
    return key_prefix + str(index)

def get_data(index):
    return data[index % ARRAY_SIZE]

for i in range(iterations):
    print(get_data(i))