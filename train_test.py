import os
import numpy as np
from sklearn.linear_model import LinearRegression, SGDRegressor
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestRegressor
import joblib
import warnings
warnings.filterwarnings('ignore')



#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Define custom transformers
class ColumnSelector(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.columns]


class DropInvalidRows(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # Apply the conditions to drop rows
        mask = ((X['PULocationID'] > 263) |
                (X['PULocationID'] < 1) |
                (X['DOLocationID'] > 263) |
                (X['DOLocationID'] < 1) |
                (X['tpep_pickup_datetime'].dt.year != 2023) |
                (X['trip_distance'] <= 0) |
                (X['fare_amount'] <= 0) |
                (X['total_amount'] <= 0) |
                (X['total_sec'] <= 0))
        return X.loc[~mask]


class AddDayNumber(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['PUdayno'] = X['tpep_pickup_datetime'].dt.day
        return X

class AddPUhour(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['PUhour'] = X['tpep_pickup_datetime'].dt.hour
        return X


class Addtotalsec(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['total_sec'] = (X['tpep_dropoff_datetime']-X['tpep_pickup_datetime']).dt.total_seconds()
        return X


class RemoveOutliers(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=2.5):
        self.threshold = threshold

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        # Compute the z-scores for the features
        z_scores = np.abs((X - X.mean()) / X.std())
        # Create a mask for rows that are not outliers
        mask = (z_scores < self.threshold).all(axis=1)
        return X[mask]









#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Define and apply the pipeline
preprocessing = Pipeline([
    ('add_day_number', AddDayNumber()),
    ('add_PUhour', AddPUhour()),
    ('add_totalsec', Addtotalsec()),
    ('drop_invalid', DropInvalidRows()),  # Drop invalid rows before any other operations
    ('column_selector', ColumnSelector(columns=['total_amount','RatecodeID','passenger_count','PULocationID','DOLocationID','trip_distance','total_sec','PUhour','PUdayno'])),
    ('imputer', SimpleImputer(strategy='median')),
    ('outlier_removal', RemoveOutliers()),
    ( 'scaler', MinMaxScaler())
    ])










#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Read the results.txt file
with open('results.txt', 'r') as file:
    lines = file.readlines()

with open('parquet_files_test.txt', 'r') as data_file:
    data_files = data_file.read().split(',')
print(data_files)
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#random forest

# Check if the first line is 1
# if int(lines[0]) == 1:
#     # Read the number of files from the second line
#     num_files = int(lines[1])
#     all_df = pd.DataFrame()

#     # Read the data from the files
#     for i in range(num_files):
#         file_path = data_files[-i]  # Assuming the file names are file1.txt, file2.txt, etc.
#         df = pd.read_parquet(file_path, engine='pyarrow')
#         df = preprocessing.fit_transform(df)
#         pd.concat([all_df,df],axis=0)

    
#     X  = all_df[:,1:]
#     y = all_df[:,0]
#     x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# RF = RandomForestRegressor(n_estimators=12,max_depth=8)
# RF.fit(x_train,y_train)


# joblib.dump(RF, 'RF_model.pkl')







print(data_files)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------
#SGDRegressor for partial_fit
# Check if the first line is 1
if int(lines[0]) == 1:
    # Read the number of files from the second line
    num_files = int(lines[1])

    SGDRegressor = SGDRegressor()
    # Read the data from the files
    for i in range(num_files,0,-1):
        file_path = data_files[i]  # Assuming the file names are file1.txt, file2.txt, etc.
        df = pd.read_parquet(file_path, engine='pyarrow')
        df = preprocessing.fit_transform(df)
        X = df[:,1:]
        y = df[:,0]
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        SGDRegressor.partial_fit(x_train,y_train)
        print('Accuracy score for the model is:',SGDRegressor.score(x_test,y_test))




print(SGDRegressor.score(x_test,y_test))
# Save the trained model
joblib.dump(SGDRegressor,'SGD_model.pkl')