import csv
import json
import time
import fdb

from benchmark.helper import load_data, generate_key, get_data, get_result_path, generate_key_mix, generate_key_doc, run, flush
from benchmark.config.parameters import ITERATIONS, ITERATIONS_MIX, ITERATIONS_JSON_DOCUMENT, FLUSH_EVERY

data = load_data()

fdb.api_version(740)
db = fdb.open()
db.get(b'_warmup')



def test_insert():
    result_path = get_result_path('insert')
    rows = []
    with open(result_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['elapsed_ms'])
        for i in range(ITERATIONS):
            key = generate_key(i).encode()
            payload = str(get_data(data, i)).encode()
            t0 = time.perf_counter()
            db.set(key, payload)
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
            key = generate_key(i).encode()
            t0 = time.perf_counter()
            db.get(key)
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
            key = generate_key(i).encode()
            payload = str(get_data(data, i)).encode()
            t0 = time.perf_counter()
            db.set(key, payload)
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
            key = generate_key(i).encode()
            t0 = time.perf_counter()
            db.clear(key)
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
            key = generate_key_mix(i).encode()
            payload = str(get_data(data, i)).encode()
            t0 = time.perf_counter()
            db.set(key, payload)
            elapsed_write = (time.perf_counter() - t0) * 1000
            t1 = time.perf_counter()
            db.get(key)
            elapsed_read = (time.perf_counter() - t1) * 1000
            rows.append(['write', elapsed_write])
            rows.append(['read', elapsed_read])
            db.clear(key)
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
                key = generate_key_mix(read_counter).encode()
                t0 = time.perf_counter()
                db.get(key)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['read', elapsed])
                read_counter += 1
            else:
                key = generate_key_mix(write_counter).encode()
                payload = str(get_data(data, write_counter)).encode()
                t0 = time.perf_counter()
                db.set(key, payload)
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
                key = generate_key_mix(write_counter).encode()
                payload = str(get_data(data, write_counter)).encode()
                t0 = time.perf_counter()
                db.set(key, payload)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['write', elapsed])
                write_counter += 1
            else:
                key = generate_key_mix(read_counter).encode()
                t0 = time.perf_counter()
                db.get(key)
                elapsed = (time.perf_counter() - t0) * 1000
                rows.append(['read', elapsed])
                db.clear(key)
                read_counter += 1
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
            key = generate_key_doc(i).encode()
            doc = json.dumps({'payload': str(get_data(data, i)), 'counter': 0, 'tags': ['tag0', 'tag1']}).encode()
            t0 = time.perf_counter()
            db.set(key, doc)
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
            key = generate_key_doc(i).encode()
            t0 = time.perf_counter()
            json.loads(db.get(key))
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
            key = generate_key_doc(i).encode()
            t0 = time.perf_counter()
            json.loads(db.get(key))['payload']
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
            key = generate_key_doc(i).encode()
            new_payload = str(get_data(data, i))
            t0 = time.perf_counter()
            doc = json.loads(db.get(key))
            doc['payload'] = new_payload
            db.set(key, json.dumps(doc).encode())
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
            key = generate_key_doc(i).encode()
            t0 = time.perf_counter()
            doc = json.loads(db.get(key))
            doc['counter'] += 1
            db.set(key, json.dumps(doc).encode())
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
            key = generate_key_doc(i).encode()
            t0 = time.perf_counter()
            db.clear(key)
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
    # queue pominieta: FDB ma twardy limit 100 KB na wartosc,
    # emulacja kolejki jako JSON array w jednym kluczu go przekracza
    'queue':             [],
    'doc_insert':        [test_doc_insert],
    'doc_read':          [test_doc_read],
    'doc_read_partial':  [test_doc_read_partial],
    'doc_update_partial':[test_doc_update_partial],
    'doc_increment':     [test_doc_increment],
    'doc_delete':        [test_doc_delete],
}

if __name__ == '__main__':
    run(CATEGORIES)