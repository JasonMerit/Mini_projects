import time
from typing import List
import concurrent.futures as cf
import multiprocessing as mp

# 2 cores
# 4 logical processors
start = time.perf_counter()

def do_something(secs, i):
    print(f"{i}) sleeping {secs} second...")
    time.sleep(secs)
    # print("done sleeping...")
    return f"{i}) done sleeping... {secs}"


if __name__ == "__main__":
    t = 1
    # Sequential CPU
    # for i in range(1):
    #     do_something(t)

    # Parallel CPU
    # processes : List[mp.Process] = []
    # for i in range(1):
    #     p = mp.Process(target=do_something, args=[t])
    #     p.start()
    #     processes.append(p)
    
    # for process in processes:
    #     process.join()

    # Parallel CPU with concurrent.futures
    # with cf.ProcessPoolExecutor() as executor:
    #     seconds = [5, 4, 3, 2, 1]
    #     results = [executor.submit(do_something, sec) for sec in seconds]
    #     for f in cf.as_completed(results):  # prnits as soon as they are done
    #         print(f.result())
    
    # Parallel CPU with concurrent.futures and map
    with cf.ProcessPoolExecutor(max_workers=4) as executor:
        seconds = [5, 4, 3, 2, 1]
        index = [0, 1, 2, 3, 4]
        results = executor.map(do_something, seconds, index)
        for result in results:  # return results in order of initiation
            print(result)



    finish = time.perf_counter()

    print(f'Finished in {round(finish-start, 2)} second(s)')