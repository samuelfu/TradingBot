import os
import pandas as pd

train_dir = 'train_data'
def load_simple(data_dir=train_dir):
    """
    returns a tuple with columns
        timesteps: ndarray representing timesteps
        prev_price: ndarray price right now you use for predictions
        x1: ndarray representing a feature
        x2: ndarray representing a feature
        next_price: ndarray price at next timestep you are trying to predict
    """
    df = pd.read_csv(os.path.join(data_dir, 'simple.csv'))
    return (df.prev_price.values, df.x1.values, df.x2.values, df.p.values)


def load_medium(data_dir=train_dir):
    """
    returns a tuple with columns
        timesteps: ndarray representing timesteps
        prev_price: ndarray price right now you use for predictions
        x1: ndarray representing a feature
        x2: ndarray representing a feature
        x3: ndarray representing a feature
        next_price: ndarray price at next timestep you are trying to predict
    """
    df = pd.read_csv(os.path.join(data_dir, 'medium.csv'))
    return (df.prev_price.values, df.x1.values, df.x2.values, df.x3.values, df.p.values)


def load_hard(data_dir=train_dir):
    """
    returns a tuple with columns
        timesteps: ndarray representing timesteps
        prev_price: ndarray price right now, included for consistency
        x1: ndarray representing a feature
        x2: ndarray representing a feature
        x3: ndarray representing a feature
        next_price: ndarray price at next timestep you are trying to predict
    Note for hard, prev_price is not sufficient and you might want to consider some type of price momentum effect
    For the actual tests, you'll receive an array of the 50 previous prices for hard
    """
    df = pd.read_csv(os.path.join(data_dir, 'hard.csv'))
    return (df.prev_price.values, df.x1.values, df.x2.values, df.x3.values, df.p.values)
