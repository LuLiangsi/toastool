import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from IPython import display
from matplotlib import pyplot as plt
from matplotlib_inline import backend_inline

import time

import sys

toast = sys.modules[__name__]

def hello_world():
    print("Hello World")

def use_svg_display():
    backend_inline.set_matplotlib_formats('svg')

def set_figsize(figsize=(3.5, 2.5)):
    use_svg_display()
    toast.plt.rcParams['figure.figsize'] = figsize

def set_axes(axes, xlabel, ylabel, xlim, ylim, xscale, yscale, legend, title=None):
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.set_xscale(xscale)
    axes.set_yscale(yscale)
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    if legend:
        axes.legend(legend)
    if title:
        axes.set_title(title)
    axes.grid()

def plot(X, Y=None, xlabel=None, ylabel=None, legend=[], xlim=None,
         ylim=None, xscale='linear', yscale='linear',
         fmts=('-', 'm--', 'g-.', 'r:'), figsize=(3.5, 2.5), axes=None):
    def has_one_axis(X):
        return (hasattr(X, 'ndim') and X.ndim == 1 or isinstance(X, list) and not hasattr(X[0], '__len__'))
    
    if has_one_axis(X):
        X = [X]
    if Y is None:
        X, Y = [[]] * len(X), X
    elif has_one_axis(Y):
        Y = [Y]
    if len(X) != len(Y):
        X = X * len(Y)
    
    set_figsize(figsize)
    if axes is None:
        axes = toast.plt.gca()
    axes.cla()
    for x, y, fmt in zip(X, Y, fmts):
        axes.plot(x, y, fmt) if len(x) else axes.plot(y, fmt)
    set_axes(axes, xlabel, ylabel, xlim, ylim, xscale, yscale, legend)

class toastPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"

class Animator:
    def __init__(self, max_iter, 
                 xlabel=None, ylabel=None, 
                 legend=None, 
                 xlim=None, ylim=None,
                 xscale='linear', yscale='linear', 
                 fmts=('-', 'm--', 'g-.', 'r:'),
                 nrows=1, ncols=1, figsize=(7, 5)):
        
        self.total = max_iter
        
        self.length = 10
        self.fill = '█'

        self.iteration = 0

        self.start_time = None
        self.last_start_time = None
        self.total_elapsed_time = 0
        self.elapsed_time = 0
        self.estimated_time = 0

        self.handle = toastPoint(0, 0)


        if legend is None:
            legend = []
        toast.use_svg_display()
        self.fig, self.axes = toast.plt.subplots(nrows, ncols, figsize=figsize)
        if nrows * ncols == 1:
            self.axes = [self.axes, ]
        self.iter_message = f"\n  \n --------------------------------- \n"
        xlim = xlim if xlim else [0, max_iter]
        self.config_axes = lambda: toast.set_axes(self.axes[0], xlabel, ylabel, xlim, ylim, xscale, yscale, legend, self.iter_message)
        self.X, self.Y, self.fmts = None, None, fmts

    def add_plot(self):
        x, y = self.handle.x, self.handle.y

        if not hasattr(y, "__len__"):
            y = [y]
        n = len(y)
        if not hasattr(x, "__len__"):
            x = [x] * n
        if not self.X:
            self.X = [[] for _ in range(n)]
        if not self.Y:
            self.Y = [[] for _ in range(n)]
        for i, (a, b) in enumerate(zip(x, y)):
            if a is not None and b is not None:
                self.X[i].append(a)
                self.Y[i].append(b)
        self.axes[0].cla()
        for x, y, fmt in zip(self.X, self.Y, self.fmts):
            self.axes[0].plot(x, y, fmt)

        self.config_axes()
        display.display(self.fig)
        display.clear_output(wait=True)


    def format_time(self, seconds):
        """将秒转换为格式化时间字符串"""
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        return f'{int(hours):02}:{int(mins):02}:{int(secs):02}'
    
    def progress_bar(self):
        percent = ("{0:.1f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '--' * (self.length - filled_length)
        # 显示进度条，迭代耗时，总耗时，和预计完成时间
        self.iter_message = f'{percent}% |{bar}| {self.iteration}/{self.total} [{self.format_time(self.total_elapsed_time)} <-- {self.format_time(self.estimated_time)}   {self.elapsed_time:.4f}s/it] '        

    def __iter__(self):
        self.start_time = time.time()
        return self

    def __next__(self):
        if self.iteration == 0:
            self.start_time = time.time()
            self.last_start_time = time.time()

            # self.progress_bar()
            # self.add_plot()

            self.iteration += 1

            self.handle.x = self.iteration
            return self.handle
        elif self.iteration < self.total:
            self.elapsed_time = time.time() - self.last_start_time
            self.total_elapsed_time = time.time() - self.start_time
            self.estimated_time = self.elapsed_time * (self.total - self.iteration)
            self.progress_bar()
            self.add_plot()

            self.iteration += 1

            self.last_start_time = time.time()
            self.handle.x = self.iteration
            return self.handle
        else:
            self.elapsed_time = time.time() - self.last_start_time
            self.total_elapsed_time = time.time() - self.start_time
            self.estimated_time = 0
            self.progress_bar()
            self.add_plot()
            raise StopIteration

