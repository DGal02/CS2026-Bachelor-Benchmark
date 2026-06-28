import csv
import json
import os
import time
from pymemcache.client.base import Client

from benchmark.helper import load_data, generate_key, get_data, get_result_path, generate_key_mix, generate_queue_key, generate_key_doc, run, flush
from benchmark.config.parameters import ITERATIONS, ITERATIONS_MIX, ITERATIONS_JSON_QUEUE_INSERTS, ITERATIONS_JSON_DOCUMENT, FLUSH_EVERY

data = load_data()

client = Client(
    (os.environ.get('MEMCACHED_HOST', 'localhost'), int(os.environ.get('MEMCACHED_PORT', 11211))),
    connect_timeout=5,
    timeout=5,
)
client.get('_warmup')



def test_insert():
    result_path = get_result_path('insert')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i)
            payload = str(get_data(data, i))
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_read():
    result_path = get_result_path('read')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i)
            t0 = time.perf_counter()
            client.get(key)
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_update():
    result_path = get_result_path('update')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS - 1, -1, -1):
            key = generate_key(i)
            payload = str(get_data(data, i))
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_delete():
    result_path = get_result_path('delete')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i)
            t0 = time.perf_counter()
            client.delete(key)
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_mix_50w_50r():
    result_path = get_result_path('mix_50W_50R')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['operation', 'elapsed_ms'])
        for i in range(ITERATIONS_MIX):
            key = generate_key_mix(i)
            payload = str(get_data(data, i))
            t0 = time.perf_counter()
            client.set(key, payload)
            elapsed_write = (time.perf_counter() - t0) * 1000
            t1 = time.perf_counter()
            client.get(key)
            elapsed_read = (time.perf_counter() - t1) * 1000
            rows.append(['write', elapsed_write])
            rows.append(['read', elapsed_read])
            client.delete(key)
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_mix_90w_10r():
    result_path = get_result_path('mix_90W_10R')
    rows = []
    write_counter = 0
    read_counter = 0
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['operation', 'elapsed_ms'])
        for i in range(ITERATIONS_MIX):
            if i % 10 == 9:
                key = generate_key_mix(read_counter)
                t0 = time.perf_counter()
                client.get(key)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['read', elapsed])
                read_counter += 1
            else:
                key = generate_key_mix(write_counter)
                payload = str(get_data(data, write_counter))
                t0 = time.perf_counter()
                client.set(key, payload)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['write', elapsed])
                write_counter += 1
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_mix_10w_90r():
    result_path = get_result_path('mix_10W_90R')
    rows = []
    write_counter = ITERATIONS_MIX * 9 // 10
    read_counter = ITERATIONS_MIX // 10
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['operation', 'elapsed_ms'])
        for i in range(ITERATIONS_MIX):
            if i % 10 == 0:
                key = generate_key_mix(write_counter)
                payload = str(get_data(data, write_counter))
                t0 = time.perf_counter()
                client.set(key, payload)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['write', elapsed])
                write_counter += 1
            else:
                key = generate_key_mix(read_counter)
                t0 = time.perf_counter()
                client.get(key)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['read', elapsed])
                client.delete(key)
                read_counter += 1
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_queue():
    result_path = get_result_path('queue')
    queue_key = generate_queue_key()
    push_counter = 0
    phase1_ops = ITERATIONS_JSON_QUEUE_INSERTS * 3 // 2
    remaining = ITERATIONS_JSON_QUEUE_INSERTS - ITERATIONS_JSON_QUEUE_INSERTS // 2
    rows = []
    client.set(queue_key, json.dumps([]))
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['operation', 'elapsed_ms'])
        for i in range(phase1_ops):
            if i % 3 != 2:
                receiver = f'test{push_counter}@test.pl'
                message = {
                    'sender': 'test@test.pl',
                    'receiver': receiver,
                    'message': f'Hello {receiver}.{get_data(data, push_counter)}.',
                }
                t0 = time.perf_counter()
                queue = json.loads(client.get(queue_key))
                queue.append(message)
                client.set(queue_key, json.dumps(queue))
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['push', elapsed])
                push_counter += 1
            else:
                t0 = time.perf_counter()
                queue = json.loads(client.get(queue_key))
                queue.pop(0)
                client.set(queue_key, json.dumps(queue))
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['pop', elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        for i in range(phase1_ops, phase1_ops + remaining):
            t0 = time.perf_counter()
            queue = json.loads(client.get(queue_key))
            queue.pop(0)
            client.set(queue_key, json.dumps(queue))
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append(['pop', elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_doc_insert():
    result_path = get_result_path('doc_insert')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS_JSON_DOCUMENT):
            key = generate_key_doc(i)
            doc = json.dumps({'payload': str(get_data(data, i)), 'counter': 0, 'tags': ['tag0', 'tag1']})
            t0 = time.perf_counter()
            client.set(key, doc)
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_doc_read():
    result_path = get_result_path('doc_read')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS_JSON_DOCUMENT):
            key = generate_key_doc(i)
            t0 = time.perf_counter()
            json.loads(client.get(key))
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_doc_read_partial():
    result_path = get_result_path('doc_read_partial')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS_JSON_DOCUMENT):
            key = generate_key_doc(i)
            t0 = time.perf_counter()
            json.loads(client.get(key))['payload']
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_doc_update_partial():
    result_path = get_result_path('doc_update_partial')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS_JSON_DOCUMENT - 1, -1, -1):
            key = generate_key_doc(i)
            new_payload = str(get_data(data, i))
            t0 = time.perf_counter()
            doc = json.loads(client.get(key))
            doc['payload'] = new_payload
            client.set(key, json.dumps(doc))
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_doc_increment():
    result_path = get_result_path('doc_increment')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS_JSON_DOCUMENT):
            key = generate_key_doc(i)
            t0 = time.perf_counter()
            doc = json.loads(client.get(key))
            doc['counter'] += 1
            client.set(key, json.dumps(doc))
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


def test_doc_delete():
    result_path = get_result_path('doc_delete')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS_JSON_DOCUMENT):
            key = generate_key_doc(i)
            t0 = time.perf_counter()
            client.delete(key)
            elapsed = (time.perf_counter() - t0) * 1000
            rows.append([elapsed])
            if len(rows) >= FLUSH_EVERY:
                flush(writer, rows)
        flush(writer, rows)


CATEGORIES = {
    'insert':            [test_insert],
    'read':              [test_read],
    'update':            [test_update],
    'delete':            [test_delete],
    'mix':               [test_mix_50w_50r, test_mix_90w_10r, test_mix_10w_90r],
    'queue':             [test_queue],
    'doc_insert':        [test_doc_insert],
    'doc_read':          [test_doc_read],
    'doc_read_partial':  [test_doc_read_partial],
    'doc_update_partial':[test_doc_update_partial],
    'doc_increment':     [test_doc_increment],
    'doc_delete':        [test_doc_delete],
}

if __name__ == '__main__':
    run(CATEGORIES)