import numpy as np
from numpy import pi, log, sin, cos, dot, e
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn import model_selection
from sklearn import preprocessing
from sklearn import metrics

#Inputs
file_path = 'C:\\Users\\liamg\\PycharmProjects\\NBApredictions\\data\\df_players.csv'
test_player = "Kyle Lowry"
features = ['PTS', 'AST', 'REB', 'BLK', 'STL', 'WS', 'ALLSTAR']

## Import Data:
df = pd.read_csv(file_path) # Pull data from the local file

# Prepare data for analysis
df.drop(axis = 1, columns = 'Unnamed: 0', inplace = True)
# Drop players who are missing basic stats:
df = df.drop(axis = 0, index = df.index[pd.isna(df.REB)]).reset_index()

# Missing values of OREB and DREB
oreb_ratio = np.asarray(df.OREB.drop(axis = 0, index = df.index[df.REB == 0]))/np.asarray(df.REB.drop(axis = 0, index = df.index[df.REB == 0])) # Obtain the average ratio of OREB to REB
oreb_ratio= oreb_ratio[~pd.isna(oreb_ratio)]
oreb_ratio = np.average(oreb_ratio)

for i, x in enumerate(df.OREB): # Replace Nan values with the player's total REB times the average OREB/REB ratio
    if pd.isna(x):
        df.loc[i,'OREB'] = int(df.loc[i,'REB']*oreb_ratio)

for i, x in enumerate(df.DREB): # Replace Nan values with the player's total REB times the average DREB/REB ratio
    if pd.isna(x):
        df.loc[i,'DREB'] = int(df.loc[i,'REB']*(1-oreb_ratio))

# Missing values of STL and BLK
df['BLK'].fillna(value = np.average(df.BLK.dropna()), inplace = True) # Replace BLK Nan values with the average BLK value
df['STL'].fillna(value = np.average(df.STL.dropna()), inplace = True) # Replace STL Nan values with the average STL value

## Create and prepare X and y datasets for testing/training
X = df[features]
y = np.asarray(df['HOF'])
X = preprocessing.StandardScaler().fit(X).transform(X) # Scale features by removing the mean and scaling to unit variance.
X = np.asarray(X)

# Find the index and stats of the test player
player_i = df.index[df.PLAYER_NAME == test_player][0]
X_player = X[player_i,:]
y_player  = y[player_i]
X = np.delete(X, obj = player_i, axis=0) # Drop the player from the training set.
y = np.delete(y, obj = player_i)

# Drop active players as they can't be in the Hall of Fame yet
active_i = df.index[df['ACTIVE?'] == 'TRUE']
X = np.delete(X, obj = active_i, axis=0) # Drop active players from the training set.
y = np.delete(y, obj = active_i)

## Logistic Regression
# Method from Scratch
# 1. Standardize the data (works for X inputs with multiple features)
def standardizer(X):
    for i in range(X.shape[1]):
        X[:, i] = (X[:, i] - np.mean(X[:, i])) / np.std(X[:, i])
    return X

# Define some metrics for accuracy:
def F1_score(y_real,y_pred):
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for i in range(len(y_real)):
        if y_real[i] & y_pred[i] == 0:
            TN = TN + 1
        if y_real[i] & y_pred[i] == 1:
            TP = TP + 1
        if y_pred[i] == 1 & y_real[i] == 0:
            FP = FP + 1
        if y_pred[i] == 0 & y_real[i] == 1:
            FN = FN + 1
    prec = TP/(TP+FP)
    recall = TP/(TP+FN)
    F1 =  2*prec*recall/(prec+recall)
    return F1

def accuracy_score(y_real,y_pred):
    suc = 0
    for i in range(len(y_real)):
        if y_real[i] == y_pred[i]:
            suc = suc + 1
    accuracy = suc/len(y_real)
    return accuracy


# Create Logistic Regression class
class LogReg:
    # 2. Initialize parameters
    def initialize(self, X):
        theta = np.zeros((X.shape[1] + 1, 1)) # weight factor for each feature
        X = np.c_[np.ones((X.shape[0], 1)), X] # concatenate column of ones to the features matrix
        return theta, X

    # 3. Define the sigmoid function
    def sigmoid(self, z): # z is defined as the dot product of the
        y = 1 / (1 + e ** (-z))
        return y

    #4. Define the cost function
    def cost(self, X, theta, y):
        z = dot(X,theta)
        cost0 = y.T.dot(log(self.sigmoid(z)))
        cost1 = (1-y).T.dot(log(1-self.sigmoid(z)))
        cost = -((cost1 + cost0))/len(y)
        return cost

    #5. Gradient Descent (for fitting function)
    def fit(self, X, y, alpha=0.001, iter=100):
        theta, X = self.initialize(X)
        cost_list = np.zeros(iter)
        for i in range(iter):
            theta = theta - alpha * dot(X.T, self.sigmoid(dot(X, theta)) - np.reshape(y, (len(y), 1)))
            cost_list[i] = self.cost(X, theta, y)
        self.theta = theta
        return cost_list

    #6. Create a Prediction Function:
    def predict(self, X):
        z = dot(self.initialize(X)[1], self.theta)
        pred_val = []
        for i in self.sigmoid(z):
            if i > 0.5:
                pred_val.append(1)
            else:
                pred_val.append(0)
        return pred_val

    def predict_proba(self, X):
        z = dot(self.initialize(X)[1], self.theta)
        pred_val = self.sigmoid(z)
        return pred_val

log_reg_man = LogReg()
model = log_reg_man.fit(X,y)
y_hat = log_reg_man.predict(X_player.reshape(1, -1))
y_prob = log_reg_man.predict_proba(X_player.reshape(1, -1))
print('The probability of ' + test_player + ' making the HOF is : %.2f %%. (Manual Method)' % (y_prob*100))

# Using Sci-kit Learn
log_reg_skl = LogisticRegression().fit(X,y)
y_hat = log_reg_skl.predict(X_player.reshape(1, -1))
print('The probability of ' + test_player + ' making the HOF is : %.2f %%. (Sklearn Method)' % (log_reg_skl.predict_proba(X_player.reshape(1, -1))[0,1]*100))
