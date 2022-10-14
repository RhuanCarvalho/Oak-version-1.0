from functools import wraps
import time

def calculeteHorMinSec(time_):

    hour_ = int(time_/3600)
    min_ = int(((time_)-(hour_*3600))/60)
    sec_ = int(((time_)-(hour_*3600)-(min_*60)))
    mili_ = int((((time_)-(hour_*3600)-(min_*60))-sec_)*1000)

    total_ = time_

    return hour_, min_, sec_, mili_, total_

def printTime(*args):
    hour_, min_, sec_, mili_, total_ = args[0]
    name = args[1]
    
    print(f'function [ {name:^40} ] -> time execution {total_:.3f} seconds [{hour_:0>2}:{min_:0>2}:{sec_:0>2}:{mili_:0>3} (hh:mm:ss:ml)]')


def calcule_time_function(function_):
    @wraps(function_)
    def wrapper(*args, **kwargs):

        init_time = time.time()
        response = function_(*args, **kwargs)
        finish_time = time.time()

        printTime(calculeteHorMinSec(finish_time - init_time), function_.__name__)

        return response

    return wrapper

if __name__== '__main__':
    # printTime(calculeteHorMinSec(26220.25), 'Teste')
    pass

