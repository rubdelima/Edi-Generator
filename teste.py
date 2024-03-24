from backend.models import loading
import time
from threading import Thread

@loading("Executando Função 1", "Função 1 Concluída")
def fn1():
    time.sleep(10)
    print("Função 1")

@loading("Executando Função 2", "Função 2 Concluída")
def fn2():
    time.sleep(5)
    print("Função 2")

if __name__ == '__main__':
    thr1 = Thread(target=fn1)
    thr2 = Thread(target=fn2)
    thr1.start()
    thr2.start()
    thr1.join()
    thr2.join()
