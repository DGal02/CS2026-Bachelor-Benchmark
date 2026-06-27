import csv
import os
import time
import redis
from benchmark.helper import load_data, generate_key, get_data, get_result_path

# temporary solution, variables
iterations = 10000
data_size = 'small'
test_result_folder = '2026-06-27-19-21-05'
# end of variables

data = load_data(data_size)

client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
)

client.flushdb()

def test_insert():
    result_path = get_result_path(test_result_folder, 'redis-insert')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(iterations):
            t0 = time.perf_counter()
            client.set(generate_key(i), get_data(data, i))
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])

if __name__ == '__main__':
    test_insert()