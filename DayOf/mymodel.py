from dayof.framework.train_loaders import load_simple, load_medium, load_hard
import numpy as np
train_dir = 'train_data'

# Implement your models below
# Test mean square error on the training set by
#   running python test_model.py (possible errors with Python2)
# Depending on your method, you might want to also consider cross 
#   validation or some type of out-of-sample performance metric

class SimpleModel(object):
    def __init__(self):
        self.prev_price, self.x1, self.x2, self.next_price = load_simple(train_dir)
        self.train()

    def train(self):
        self.b0 = .1749575
        self.b1 = .9995143
        self.b2 = -.0972899
        self.b3 = .0076197
        pass

    def predict(self, prev_price, x1, x2):
        return self.b0+prev_price*self.b1+x1*self.b2+x2*self.b3

class MediumModel(object):
    def __init__(self):
        self.prev_price, self.x1, self.x2, self.x3, self.next_price = load_medium(train_dir)
        self.train()

    def train(self):
        # train model here
        pass

    def predict(self, prev_price, x1, x2, x3):
        return prev_price

class HardModel(object):
    def __init__(self):
        self.prev_price, self.x1, self.x2, self.x3, self.next_price = load_hard(train_dir)
        self.train()

    def train(self):
        # train model here
        pass

    def predict(self, price_history, x1, x2, x3):
        # note price history is the previous 50 prices with most recent prev_price last
        #   and x1, x2, x3 are still single values
        return price_history[-1]


simple_model = SimpleModel()
medium_model = MediumModel()
hard_model = HardModel()

def allocate(simple_args, medium_args, hard_args):
    """
    Implement your allocation function here
    You should return a tuple (a1, a2, a3), where
        a1 is the quantity of stock simple you wish to purchase and so forth
    You will buy the stocks at the current price
    
    The argument format is as follows:
        simple_args will be a tuple of (current_price, current_x1, current_x2)
        medium_args will be a tuple of (current_price, current_x1, current_x2, current_x3)
        hard_args will be a tuple of (current_price_history, current_x1, current_x2, current_x3)
            where the current_price_history is the previous 50 prices
            and the current price is the last element of current_price_history

    Note that although we notate for example feature x1 for all the stocks, the 
        features for each stock are unrelated (x1 for simple has no relation to x1 for medium, etc)

    Make sure the total money you allocate satisfies
        (a1 * simple_current_price + a2 * medium_current_price + a3 * hard_current_price) < 100000000
    Quantities may be decimals so don't worry about rounding
    To be safe, you should make sure you're lower than 100000000 by a threshold
    You can check your code with the provided helper test_allocate.py

    Test your allocation function on the provided test set by running python test_allocate.py
    Generate your final submission on the real data set by running python run_allocate.py
    """
    # Sample: retrieve prices and get predictions from models
    simple_price = simple_args[0]
    medium_price = medium_args[0]
    hard_price = hard_args[0][-1]

    simple_prediction = simple_model.predict(*simple_args)
    medium_prediction = medium_model.predict(*medium_args)
    hard_prediction = hard_model.predict(*hard_args)

    # Sample: allocate all money (except a small threshold) to medium
    return ((1000000000-1)/simple_prediction, 0, 0)