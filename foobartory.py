
import argparse
from collections import namedtuple
from dataclasses import dataclass
import random
import sys
from time import sleep

Foo = namedtuple('Foo', ['foo_id'])
Bar = namedtuple('Bar', ['bar_id'])
Foobar = namedtuple('Foobar', ['foo_id', 'bar_id'])
Task = namedtuple('Task', ['name', 'time_range', 'init', 'result'])

def do_nothing(*args, **kwargs):
    return []

def create_foo(storage, *args, **kwargs):
    storage.max_foo_id += 1
    storage.foo.append(Foo(storage.max_foo_id))

def create_bar(storage, *args, **kwargs):
    storage.max_bar_id += 1
    storage.bar.append(Bar(storage.max_bar_id))

def init_foobar(storage, *args, **kwargs):
    return storage.foo.pop(), storage.bar.pop()

def create_foobar(storage, foo, bar):
    storage.foobar.append(Foobar(foo.foo_id, bar.bar_id)) 

def init_sell(storage):
    storage.foobar.pop()
    return []

def sell_foobar(storage, *args, **kwargs):
    storage.currency += 10

def init_buy(storage):
    storage.currency -= 3
    for _ in range(6):
        storage.foo.pop()
    return []

def buy_robot(storage):
    storage.robots.append(Robot(storage))

TASKS = [
    Task('mining foo', (1, 1), do_nothing, create_foo),
    Task('mining bar', (0.5, 2), do_nothing, create_bar),
    Task('creating foobar', (2, 2), init_foobar, create_foobar),
    Task('selling', (10, 10), init_sell, sell_foobar),
    Task('buying', (0, 0), init_buy, buy_robot),
]

class Robot():
    robot_count = 0

    def __init__(self, storage):
        Robot.robot_count += 1
        self.name = f'ROBOT #{Robot.robot_count}'
        self.work_time = 0
        self.task_time = 0
        self.current_task = None
        self.storage = storage
        self.resources = None

    def choose_task(self):
        weights = [30,15,40,1,20]
        if not self.storage.foo or not self.storage.bar:
            weights[2] = 0
        if not self.storage.foobar:
            weights[3] = 0
        if self.storage.currency < 3 or len(self.storage.foo) < 6:
            weights[4] = 0
        self.current_task = random.choices(TASKS, weights=weights).pop()

    def start_task(self):
        self.choose_task()
        self.resources = self.current_task.init(self.storage)
        self.task_time = random.uniform(*self.current_task.time_range)
        print(f'{self.name} started {self.current_task.name}')

    def work(self):
        if not self.current_task:
            self.start_task()
        else:
            self.work_time += 0.1
            if self.work_time >= self.task_time:
                self.complete_task()

    def complete_task(self):
        self.current_task.result(self.storage, *self.resources)
        print(f'{self.name} finished {self.current_task.name} after {round(self.work_time, 1)}s')
        self.current_task = None
        self.work_time = 0
        self.task_time = 0
        print(f'Current storage: Currency:{self.storage.currency}, Foo:{len(self.storage.foo)}, '\
                f'Bar:{len(self.storage.bar)}, Robots:{len(self.storage.robots)}')

@dataclass
class Storage:
    currency = 0
    robots = list()
    foo = list()
    max_foo_id = 0
    bar = list()
    max_bar_id = 0
    foobar = list()


def main(speed):
    print('Creating initial storage. Two worket bots have been dispatched.')
    storage = Storage()
    storage.robots.append(Robot(storage))
    storage.robots.append(Robot(storage))

    print('Worker bots have started their activities.')
    while len(storage.robots) < 30:
        for robot in storage.robots:
            robot.work()
            sleep(0.1 * speed)

    print('Maximum robot capacity exceeded: End of operations.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Working bot simulation.')
    parser.add_argument('speed', type=float, default=0.0, nargs='?',
            help='A float that represents simulation Speed. Default is zero, '\
                    'meaning the bot work time will be instant compared to '\
                    'real time. A speed under 1 will be faster while above 1 '\
                    'will be slower.')
    main(abs(parser.parse_args().speed))
