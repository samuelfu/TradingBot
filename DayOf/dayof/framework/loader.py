import os
try:
    import numpy as np
    import pandas as pd
except ImportError as e:
    print("Error: Please install numpy and pandas on your system for our loaders to work correctly on your system")
    raise e

def mean_squared_error(yhat, y):
    return 1 / len(y) * (yhat - y).dot(yhat - y)

class Grader (object):
    def __init__(self, train_dir='train_data'):
        self.data_dir = train_dir
        self.simplef = os.path.join(train_dir, 'simple.csv')
        self.mediumf = os.path.join(train_dir, 'medium.csv')
        self.hardf = os.path.join(train_dir, 'hard.csv')
        self.simpledf = self.load_train_simple()
        self.mediumdf = self.load_train_medium()
        self.harddf = self.load_train_hard()

    def simple_answers(self):
        return (self.simpledf.p.values)

    def medium_answers(self):
        return (self.mediumdf.p.values)

    def hard_answers(self):
        return (self.harddf.p.values)

    def simple_args(self):
        return (self.simpledf.prev_price.values, self.simpledf.x1.values, self.simpledf.x2.values, self.simpledf.p.values)

    def medium_args(self):
        return (self.mediumdf.prev_price.values, self.mediumdf.x1.values, self.mediumdf.x2.values, self.mediumdf.x3.values, self.mediumdf.p.values)

    def hard_args(self):
        return (self.harddf.prev_price.values, 
                self.harddf.x1.values,
                self.harddf.x2.values,
                self.harddf.x3.values,
                self.harddf.p.values)

    def load_train_simple(self):
        return pd.read_csv(self.simplef)

    def load_train_medium(self):
        return pd.read_csv(self.mediumf)

    def load_train_hard(self):
        return pd.read_csv(self.hardf)
