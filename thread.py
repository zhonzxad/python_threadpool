#!/usr/bin/env python
# -*- coding:utf-8 -*-
 
import multiprocessing
import threading
import time

try:
    import Queue as queue  # Python 2
except ImportError:
    import queue as queue  # Python 3

StopTask = object()
cpu_core_num = multiprocessing.cpu_count()

class threadpool():
    def __init__(self, max_workers=cpu_core_num):
        self.task = queue.Queue()
        self.max_workers = max_workers
 
        self.generate_list = []
        self.free_list = []
 
        self.isterminal = False

    def __del__(self):
        pass # 析构
 
    def run(self, func, args, callback=None):
        """
        线程池启动函数
        :param func: 函数名称
        :param args: 函数参数
        :param callback: 回调函数
        :return:
        """
        task = (func, args, callback)
        self.task.put(task)
 
        if len(self.free_list) == 0 and len(self.generate_list) < self.max_workers:
            self.generate_thread()
 
    def generate_thread(self):
        """创建线程"""
        t = threading.Thread(target=self.call)
        t.start()
 
    def call(self):
        """执行线程"""
        current_thread = threading.currentThread
        self.generate_list.append(current_thread)
 
        get_task = self.task.get()
        while get_task != StopTask:
            # 执行任务
            func, args, callback = get_task
            try:
                ret = func(*args)
                status = True
            except Exception as e:
                ret = e
                status = False
            
            # 执行回调函数
            if callback:
                try:
                    callback(status, ret)
                except Exception:
                    pass

            # 处理任务or立即终止
            if self.isterminal:
                # 立即终止
                get_task = StopTask
            else:
                # 空闲处理
                self.free_list.append(current_thread)
                get_task = self.task.get()
                self.free_list.remove(current_thread)
        else:
            # 销毁线程
            self.generate_list.remove(current_thread)
 
    def close(self):
        """
        等待任务全部完成后，清空所有线程
        :return:
        """
        num = len(self.generate_list)
        while num:
            self.task.put(StopTask)
            num -= 1
 
    def terminal(self):
        """
        立即终止所有的线程
        :return:
        """
        self.isterminal = True
 
        while self.generate_list:
            self.task.put(StopTask)
 
        self.task.empty()

    def worker_state(self, state_list, worker_thread):
        """
        用于记录线程中正在等待的线程数
        """
        state_list.append(worker_thread)
        try:
            yield
        finally:
            state_list.remove(worker_thread)


def func(i):
    """
    待处理任务
    :param i:
    :return:
    """
    time.sleep(0.5)
    print(i)
 
 
def call(status, ret):
    """
    回调函数
    :param status: True:任务运行无误；False：报异常
    :param ret: 任务运行返回值/异常信息
    :return:
    """
    pass
 
 
if __name__ == '__main__':
    #创建线程池
    pool = threadpool(5)
    #执行任务
    for i in range(20):
        pool.run(func, args=(i,), callback=call)
    #终止任务
    pool.close()
