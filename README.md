# NBA Stats Acquisition and Hall of Fame Probability Predictions.
Personal project to create a comprehensive database containing all NBA players, their stats and accolades and to predict the probability of each player making the hall of fame using a logistic regression model.

## Files and order of operation:
Currently, the repository contains four python files:
1. NBA_player_stats_acquision.py
      Webscrapes data on both the player's accolades and player's stats for each season played in the NBA/ABA and stores them into seperated MySQL databases.

2. nba_data_cleanser.py
      Cleans the data in the player statistics databases to fill missing values.

3. nba_accolades.py
      Aggregates the statistics from each season for every player to obtain the player's total career stats. The player's career stats and accolades are saved in a single table.

4. nba_hof_predictor.py
      Uses the table created in nba_accolades to train a logistic regression model. The model then predicts the probability of each NBA player making the hall of fame and stores theses in a table which is saved to a MySQL database.
