import numpy as np
from numpy import pi, log, sin, cos, dot, e
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from alive_progress import alive_bar
from sklearn.linear_model import LogisticRegression
from sklearn import model_selection
from sklearn import preprocessing
from sklearn import metrics

## Inputs
test_player = "Kevin Durant"
test_all = True # test all players in the source data frame.
tablename_d = 'hof_probability'
features = ['PTS', 'AST', 'TRB', 'BLK', 'STL', 'WS', 'allstar', 'allnba', 'mvp']

# MySQL Credentials
hostname = "localhost"
uname = "root"
pwd = "Sara!091996"
dbname = "nba_statistics" # Source database
tablename_s = 'nba_accolades_db'

# Import nba_seasons_db data from the database:
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
df = pd.read_sql(sql = tablename_s, con = engine).set_index('index')

plt.plot()
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

# Test for given test player:
if test_all == False:
    ## Create and prepare X and y datasets for testing/training
    X = df[features]
    y = np.asarray(df['hof'])
    X = preprocessing.StandardScaler().fit(X).transform(X) # Scale features by removing the mean and scaling to unit variance.
    X = np.asarray(X)

    # Find the index and stats of the test player
    player_i = df.index[df.player_name == test_player][0]
    X_player = X[player_i,:]
    y_player  = y[player_i]
    X = np.delete(X, obj = player_i, axis=0) # Drop the player from the training set.
    y = np.delete(y, obj = player_i)

    # PLayers which have played in the last 4 years as they are inelligible for the hall of fame.
    active_i = df.index[df.last_played > date.today().year - 4]
    X = np.delete(X, obj = active_i, axis=0) # Drop active players from the training set.
    y = np.delete(y, obj = active_i)

    log_reg_man = LogReg()
    model = log_reg_man.fit(X,y)
    y_hat = log_reg_man.predict(X_player.reshape(1, -1))
    y_prob = log_reg_man.predict_proba(X_player.reshape(1, -1))
    print('The probability of ' + test_player + ' making the HOF is : %.2f %%. (Manual Method)' % (y_prob*100))

    # Using Sci-kit Learn
    log_reg_skl = LogisticRegression().fit(X,y)
    y_hat = log_reg_skl.predict(X_player.reshape(1, -1))
    print('The probability of ' + test_player + ' making the HOF is : %.2f %%. (Sklearn Method)' % (log_reg_skl.predict_proba(X_player.reshape(1, -1))[0,1]*100))

# Test for all players:
if test_all == True:
    df_all = pd.DataFrame()
    df_all[['player_name','first_played','last_played']] = df[['player_name','first_played','last_played']]
    df_all[['hof_skl']] = 0
    df_all[['hof_scr']] = 0
    with alive_bar(len(df_all.player_name), force_tty=True) as bar:
        for i, test_player in enumerate(df_all.player_name):
            ## Create and prepare X and y datasets for testing/training
            X = df[features]
            y = np.asarray(df['hof'])
            X = preprocessing.StandardScaler().fit(X.values).transform(X.values)  # Scale features by removing the mean and scaling to unit variance.
            X = np.asarray(X)

            # Find the index and stats of the test player
            player_i = df.index[df.player_name == test_player][0]
            X_player = X[player_i, :]
            y_player = y[player_i]
            X = np.delete(X, obj=player_i, axis=0)  # Drop the player from the training set.
            y = np.delete(y, obj=player_i)

            # PLayers which have played in the last 4 years as they are inelligible for the hall of fame.
            active_i = df.index[df.last_played > date.today().year - 4]
            X = np.delete(X, obj=active_i, axis=0)  # Drop active players from the training set.
            y = np.delete(y, obj=active_i)

            log_reg_scr = LogReg()
            model = log_reg_scr.fit(X, y)
            y_hat_scr = log_reg_scr.predict(X_player.reshape(1, -1))
            y_prob_scr = log_reg_scr.predict_proba(X_player.reshape(1, -1))[0]*100
            df_all.loc[i,'hof_scr'] = y_prob_scr

            # Using Sci-kit Learn
            log_reg_skl = LogisticRegression().fit(X, y)
            y_hat = log_reg_skl.predict(X_player.reshape(1, -1))
            y_prob_skl = log_reg_skl.predict_proba(X_player.reshape(1, -1))[0, 1] * 100
            df_all.loc[i, 'hof_skl'] = y_prob_skl
            bar()

    df_all = df_all.sort_values('hof_skl', ascending= False).reset_index(drop = True)
    print(df_all)
    df_all.to_sql(con=engine, name=tablename_d, if_exists='replace')
