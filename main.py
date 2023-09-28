import multiprocessing as mp
import time

def auto_daily_debit():
    while True:
        print('debit')
        time.sleep(1)

def main():
    time.sleep(5)
    raise ValueError()


if __name__ == '__main__':
    p = mp.Process(target=auto_daily_debit, daemon=True)
    p.start()
    main()
