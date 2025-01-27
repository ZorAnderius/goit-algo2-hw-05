import json
import re
import timeit
from datasketch import HyperLogLog

def is_valid_ip(ip: str) -> bool:
    reg = r'^(?:\d{1,3}\.){3}\d{1,3}$'
    return bool(re.match(reg, ip))

def upload_log(file_path: str) -> list:
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            try:
                if line == "" or line == "\n":
                    continue
                log_entry = json.loads(line)
                ip = log_entry.get('remote_addr')
                if ip and is_valid_ip(ip):
                    data.append(ip)
            except json.JSONDecodeError:
                continue
    return data

def count_unique_ips_hll(data: list) -> float:
    hll = HyperLogLog(10)
    for ip in data:
        hll.update(ip.encode('utf-8'))
    return hll.count()

def count_unique_ips_set(data: list) -> int:
    unique_ips = set()
    for ip in data:
        unique_ips.add(ip)
    return len(unique_ips)

if __name__ == "__main__":
    file_path = 'lms-stage-access.log'
    data = upload_log(file_path)

    exact_count = count_unique_ips_set(data)
    exact_time = timeit.timeit(lambda: count_unique_ips_set(data), number=100)

    hll_count = count_unique_ips_hll(data)
    hll_time = timeit.timeit(lambda: count_unique_ips_hll(data), number=100)

    print("Результати порівняння:")
    print(f"{'':<20} | {'Точний підрахунок':<20} | {'HyperLogLog':<20}")
    print(f"{'-'*70}")
    print(f"{'Унікальні елементи':<20} | {exact_count:<20} | {hll_count:<20}")
    print(f"{'Час виконання (сек.)':<20} | {exact_time:<20.2f} | {hll_time:<20.2f}")
