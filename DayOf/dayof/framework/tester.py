import os
from collections import OrderedDict
try:
    import mymodel
    if not hasattr(mymodel, 'allocate'):
        print('Module mymodel must implement function allocate()')
except ImportError as e:
    print('Error: please implement allocate in file tester.py')
    raise e

try:
    import numpy as np
    import pandas as pd
except ImportError as e:
    print("Error: Please install numpy and pandas on your system for our loaders to work correctly on your system")
    raise e


class Tester(object):
    def __init__(self, allocate_func, test_dir='test_data', output='output.csv'):
        self.allocate_func = allocate_func
        self.data_dir = test_dir
        self.output = output
        self.simple_fname = os.path.join(test_dir, 'simple.csv')
        self.medium_fname = os.path.join(test_dir, 'medium.csv')
        self.hard_fname = os.path.join(test_dir, 'hard.csv')
        self.simple_df = pd.read_csv(self.simple_fname)
        self.medium_df = pd.read_csv(self.medium_fname)
        self.hard_df = pd.read_csv(self.hard_fname)
        self.timesteps = len(self.simple_df)
        self.total = 100000000

    def test(self):
        total = self.total
        a1 = np.empty(self.timesteps, dtype=np.float64)
        a2 = np.empty(self.timesteps, dtype=np.float64)
        a3 = np.empty(self.timesteps, dtype=np.float64)
        for i in range(self.timesteps):
            price_history = np.array([np.float64(s) for s in self.hard_df.price_history[i].split()])
            args = [
                (self.simple_df.prev_price.values[i], self.simple_df.x1.values[i], self.simple_df.x2.values[i]),
                (self.medium_df.prev_price.values[i], self.medium_df.x1.values[i], self.medium_df.x2.values[i], self.medium_df.x3.values[i]),
                (price_history, 
                    self.hard_df.x1.values[i],
                    self.hard_df.x2.values[i],
                    self.hard_df.x3.values[i])]
            x1, x2, x3 = self.allocate_func(*args)
            p1 = self.simple_df.prev_price.values[i]
            p2 = self.medium_df.prev_price.values[i]
            p3 = price_history[-1]
            if (x1 < 0 or x2 < 0 or x3 < 0):
                raise ValueError("Can't spend negative money")
            if (p1 * x1 + p2 * x2 + p3 * x3 > total):
                raise ValueError("Trying to spend more money than you have")
            a1[i] = x1
            a2[i] = x2
            a3[i] = x3

        result = pd.DataFrame.from_dict(OrderedDict([
            ('a1', a1),
            ('a2', a2),
            ('a3', a3)
        ]))
        result.to_csv(self.output, index=False)

    @staticmethod
    def quantity_func(n):
        alpha = .0002
        return 2 / alpha * (np.sqrt(1 + alpha * n) - 1)

    def grade(self):
        total = self.total
        odf = pd.read_csv(self.output)
        r1, r2, r3 = self.simple_df, self.medium_df, self.hard_df
        a1 = odf.a1.values
        a2 = odf.a2.values
        a3 = odf.a3.values
        prev1, prev2 = r1.prev_price.values, r2.prev_price.values
        prev3 = np.empty((len(prev1),), dtype=np.float64)
        for i in range(len(prev1)):
            price_history = np.array([np.float64(s) for s in r3.price_history[i].split()])
            prev3[i] = price_history[-1]
        next1, next2, next3 = r1.p.values, r2.p.values, r3.p.values
        ret = 0
        for i in range(len(prev1)):
            if (prev1[i] * a1[i] + prev2[i] * a2[i] + prev3[i] * a3[i] > total):
                print('Trying to spend more than you have: trade not executed')
            elif (a1[i] < 0 or a2[i] < 0 or a3[i] < 0):
                print('Trying to spend negative money: trade not executed')
            else:
                d1, d2, d3 = next1[i] - prev1[i], next2[i] - prev2[i], next3[i] - prev3[i]
                qa1, qa2, qa3 = self.quantity_func(a1[i]), self.quantity_func(a2[i]), self.quantity_func(a3[i])
                ret += qa1 * d1 + qa2 * d2 + qa3 * d3

        print('Total Return: ' + str(ret))
        print('Average Return: ' + str(ret / len(prev1)))
        return ret