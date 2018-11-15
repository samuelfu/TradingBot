import pandas as pd
from pandas import DataFrame
from sklearn import linear_model
import statsmodels.api as sm

data = pd.read_csv('train_data/simple.csv')
df = DataFrame(data, columns=['p', 'prev_price', 't', 'x1', 'x2'])



X = df[['x1', 'x2']]
Y = df['']

print(df)