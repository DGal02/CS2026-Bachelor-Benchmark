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


def test_insert():
    result_path = get_result_path(test_result_folder, 'redis-insert')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(iterations):
            key = generate_key(i)
            payload = get_data(data, i)
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])

def test_read():
    result_path = get_result_path(test_result_folder, 'redis-read')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(iterations):
            key = generate_key(i)
            t0 = time.perf_counter()
            client.get(key)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])

def test_delete():
    result_path = get_result_path(test_result_folder, 'redis-delete')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(iterations):
            key = generate_key(i)
            t0 = time.perf_counter()
            client.delete(key)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])

if __name__ == '__main__':
    test_insert()
    test_read()
    test_delete()