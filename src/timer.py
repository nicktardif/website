import datetime

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Timer(metaclass=Singleton):
    def __init__(self):
        self.times = {}

    def run(self, name, method):
        start_time = datetime.datetime.now()
        method()
        end_time = datetime.datetime.now()

        total_time = (end_time - start_time).total_seconds()
        self.times[name] = total_time
        
    def print_times(self):
        print('\nRuntimes')
        total_time = 0
        for key in self.times:
            current_time = self.times[key]
            self.__print_time(key, current_time)
            total_time = total_time + current_time

        self.__print_time('Total', total_time)

    def __print_time(self, name, length):
        print('{:25s} {:.2f} seconds'.format(name, length))

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        Timer().run(func.__name__, lambda: func(*args, **kwargs))

    return wrapper
