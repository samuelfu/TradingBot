try:
    import numpy as np
except ImportError as e:
    print('Please install numpy')
    raise e
from mymodel import SimpleModel, MediumModel, HardModel
from dayof.framework.loader import Grader, mean_squared_error

if __name__ == '__main__':
    g = Grader()
    choice = int(input("What would you like to test?\n1) Simple\n2) Medium\n3) Hard\n4) All\n>> "))

    if choice == 1 or choice == 4:
        model = SimpleModel()
        prev_prices, x1, x2, current_prices = g.simple_args()
        predictions = []
        actuals = []
        for i in range(len(x1)):
            predictions.append(model.predict(prev_prices[i], x1[i], x2[i]))
            actuals.append(current_prices[i])
        predictions, actuals = np.array(predictions, dtype=np.float64), np.array(actuals, dtype=np.float64)
        print("Mean Squared Error for Simple Model: " + str(mean_squared_error(predictions, actuals)))

    if choice == 2 or choice == 4:
        model = MediumModel()
        prev_prices, x1, x2, x3, current_prices = g.medium_args()
        predictions = []
        actuals = []
        for i in range(len(x1)):
            predictions.append(model.predict(prev_prices[i], x1[i], x2[i], x3[i]))
            actuals.append(current_prices[i])
        predictions, actuals = np.array(predictions, dtype=np.float64), np.array(actuals, dtype=np.float64)
        print("Mean Squared Error for Medium Model: " + str(mean_squared_error(predictions, actuals)))

    if choice == 3 or choice == 4:
        model = HardModel()
        prev_prices, x1, x2, x3, current_prices = g.hard_args()
        predictions = []
        actuals = []
        for i in range(len(x1) - 50):
            k = i + 50
            price_history = prev_prices[k-49:k+1]
            predictions.append(model.predict(price_history, x1[i], x2[i], x3[i]))
            actuals.append(current_prices[k])
        predictions, actuals = np.array(predictions, dtype=np.float64), np.array(actuals, dtype=np.float64)
        print("Mean Squared Error for Hard Model: " + str(mean_squared_error(predictions, actuals)))
