import time
from concurrent.futures import ThreadPoolExecutor

def call_api(url):
    time.sleep(1)
    return {"result": f"{url} called"}

if __name__ == "__main__":
    start_time = time.time()

    urls = [
        "cam",
        "detect",
        "track",
        "search"
    ]

    executor = ThreadPoolExecutor(12)
    futures = []

    for url in urls:
        future = executor.submit(call_api,url)
        futures.append(future)
    
    for future in futures:
        print(future.result())

    elapsed = time.time() - start_time
    print(f"Elapsed: {elapsed:.2f}s")