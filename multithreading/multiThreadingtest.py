import threading
from queue import Queue


class TestClass:
    
    
    def __init__(self):
        self.a = 1
        self.infoqueue = Queue(4)
        self.flag = False
    def run(self, b):
        self.a *= b
        print(threading.currentThread() + " : " + str(self.a))
        if(self.a >= 100000):
            self.flag = True
    def work(self):
        if self.flag:
            print("work")
            self.a = 1
            print(threading.currentThread() + " : " + str(self.a))
        
        
class subRunThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        pass
flag = False
num = 1

def run(event, b):
    global flag, num
    while(True):
        num *= b
        print(threading.currentThread().name + ": " + str(num))
        if num >= 1000:
            event.clear()  # set False
            event.wait()   # True normal  False 阻塞

if __name__ == "__main__":
    event_obj = threading.Event()  # 创建一个事件
    event_obj.set()  # True
    print(event_obj.is_set())
    runThread1 = threading.Thread(target=run, args=(event_obj, 2), name="sub1")
    # runThread2 = threading.Thread(target=run, args=(event_obj, 3), name="sub2")
    runThread1.start()
    # runThread2.start()
    while(True):
        if not event_obj.is_set():  # 如果阻塞
            num = 1
            print(threading.currentThread().name + ": " + str(num))
            event_obj.set()  # 不阻塞
        else:
            pass