import csv
import json
import os
import time
import redis
from benchmark.helper import load_data, generate_key, get_data, get_result_path, generate_key_mix, generate_queue_key
from benchmark.config.parameters import ITERATIONS, ITERATIONS_JSON_QUEUE_INSERTS, TEST_CATEGORY

data = load_data()

client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
)


def test_insert():
    result_path = get_result_path('insert')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i)
            payload = get_data(data, i)
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])


def test_read():
    result_path = get_result_path('read')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i)
            t0 = time.perf_counter()
            client.get(key)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])


def test_update():
    result_path = get_result_path('update')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(ITERATIONS - 1, -1, -1):
            key = generate_key(i)
            payload = get_data(data, i)
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])


def test_delete():
    result_path = get_result_path('delete')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i)
            t0 = time.perf_counter()
            client.delete(key)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, elapsed])


def test_mix_50w_50r():
    result_path = get_result_path('mix_50W_50R')

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'operation', 'elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key_mix(i)
            payload = get_data(data, i)
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed_write = (time.perf_counter() - t0) * 1000
            t1 = time.perf_counter()
            client.get(key)
            elapsed_read = (time.perf_counter() - t1) * 1000
            writer.writerow([i, 'write', elapsed_write])
            writer.writerow([i, 'read', elapsed_read])
            client.unlink(key)


def test_mix_90w_10r():
    result_path = get_result_path('mix_90W_10R')

    write_counter = 0
    read_counter = 0

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'operation', 'elapsed_ms'])
        for i in range(ITERATIONS):
            if i % 10 == 9:
                key = generate_key_mix(read_counter)
                t0 = time.perf_counter()
                client.get(key)
                elapsed = (time.perf_counter() - t0) * 1000
                writer.writerow([i, 'read', elapsed])
                read_counter += 1
            else:
                key = generate_key_mix(write_counter)
                payload = get_data(data, write_counter)
                t0 = time.perf_counter()
                client.set(key, payload)
                elapsed = (time.perf_counter() - t0) * 1000
                writer.writerow([i, 'write', elapsed])
                write_counter += 1


def test_mix_10w_90r():
    result_path = get_result_path('mix_10W_90R')

    write_counter = ITERATIONS * 9 // 10
    read_counter = ITERATIONS // 10

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'operation', 'elapsed_ms'])
        for i in range(ITERATIONS):
            if i % 10 == 0:
                key = generate_key_mix(write_counter)
                payload = get_data(data, write_counter)
                t0 = time.perf_counter()
                client.set(key, payload)
                elapsed = (time.perf_counter() - t0) * 1000
                writer.writerow([i, 'write', elapsed])
                write_counter += 1
            else:
                key = generate_key_mix(read_counter)
                t0 = time.perf_counter()
                client.get(key)
                elapsed = (time.perf_counter() - t0) * 1000
                writer.writerow([i, 'read', elapsed])
                client.unlink(key)
                read_counter += 1



def test_queue():
    result_path = get_result_path('queue')
    queue_key = generate_queue_key()
    push_counter = 0
    phase1_ops = ITERATIONS_JSON_QUEUE_INSERTS * 3 // 2
    remaining = ITERATIONS_JSON_QUEUE_INSERTS - ITERATIONS_JSON_QUEUE_INSERTS // 2

    with open(result_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['index', 'operation', 'elapsed_ms'])

        for i in range(phase1_ops):
            if i % 3 != 2:
                receiver = f'test{push_counter}@test.pl'
                message = json.dumps({
                    'sender': 'test@test.pl',
                    'receiver': receiver,
                    'message': f'Hello {receiver}.{get_data(data, push_counter)}.',
                })
                t0 = time.perf_counter()
                client.rpush(queue_key, message)
                elapsed = (time.perf_counter() - t0) * 1000
                writer.writerow([i, 'push', elapsed])
                push_counter += 1
            else:
                t0 = time.perf_counter()
                client.lpop(queue_key)
                elapsed = (time.perf_counter() - t0) * 1000
                writer.writerow([i, 'pop', elapsed])

        for i in range(phase1_ops, phase1_ops + remaining):
            t0 = time.perf_counter()
            client.lpop(queue_key)
            elapsed = (time.perf_counter() - t0) * 1000
            writer.writerow([i, 'pop', elapsed])


INSERT_TESTS = [test_insert]
READ_TESTS = [test_read]
UPDATE_TESTS = [test_update]
DELETE_TESTS = [test_delete]
MIX_TESTS = [test_mix_50w_50r, test_mix_90w_10r, test_mix_10w_90r]
QUEUE_TESTS = [test_queue]

TEST_CATEGORIES = [INSERT_TESTS, READ_TESTS, UPDATE_TESTS, DELETE_TESTS, MIX_TESTS, QUEUE_TESTS]

CATEGORIES = {
    'insert': INSERT_TESTS,
    'read':   READ_TESTS,
    'update': UPDATE_TESTS,
    'delete': DELETE_TESTS,
    'mix':    MIX_TESTS,
    'queue':  QUEUE_TESTS,
}

if __name__ == '__main__':
    tests = CATEGORIES[TEST_CATEGORY] if TEST_CATEGORY in CATEGORIES else [t for g in TEST_CATEGORIES for t in g]
    for test in tests:
        test()
