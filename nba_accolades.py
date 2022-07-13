## NBA Accolades Database Builder
# Code which compiles the career stats and accolades for each NBA player into a single database.

# Import Packages
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
from alive_progress import alive_bar
import numpy as np
import pyautogui
import requests
import pandas as pd

# Inputs:
tablename_sa = 'nba_accolades_db' # Source table (accolades)
tablename_sp = 'nba_players_db' # Source table (player stats)
tablename_d = 'nba_db' # Destination table

# MySQL Credentials
hostname = "localhost"
uname = "root"
pwd = "rootroot"
dbname = "nba_statistics"



# Import nba_seasons_db data from the database:
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
query = 'select * from' \
        '(select player_name as player_name_i, birth_year as birth_year_i, min(Season), max(Season), sum(G), sum(GS), sum(MP), sum(FG), sum(FGA), sum(3P), sum(3PA), sum(2P), sum(2PA),' \
        'sum(FT), sum(FTA), sum(ORB), sum(DRB), sum(TRB), sum(AST), sum(STL),sum(BLK), sum(TOV), sum(PF), sum(PTS), sum(OWS),'\
        'sum(DWS), SUM(WS), sum(OBPM), sum(DBPM), sum(BPM) from %s group by player_name, birth_year) as dummy_table ' \
        'left join %s ' \
        'on dummy_table.player_name_i = %s.player_name and dummy_table.birth_year_i = %s.birth_year' % (tablename_sp,tablename_sa,tablename_sa, tablename_sa) # Query to obtain the desired data from the database.
df = pd.read_sql(sql = query, con = engine)
df = df.drop(columns = ['player_name','index', 'birth_year'])

df.columns = ['player_name', 'birth_year', 'first_played', 'last_played', 'G', 'GS', 'MP', 'FG', 'FGA', '3P', '3PA', '2P', '2PA', 'FT', 'FTA', 'ORB',
              'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'OWS', 'DWS', 'WS', 'OBPM', 'DBPM', 'BPM','champ', 'mvp',
              'fmvp', 'allstar', 'allnba', 'alldef', 'hof'] # Rename the columns of the dataFrame

# Print the DataFrame.
print(df.sort_values('PTS',ascending= False)[df.columns])
print(df[['player_name','PTS', 'WS','champ','allstar','hof']].sort_values('WS',ascending= False).head(15))
print(df.columns)



# Create dialog box to confirm the saving of the file
conf = pyautogui.confirm('Save Dataframe to file?')

# Save the DataFrame to file.
if conf == 'OK':
    # Save the DataFrame to a MySQL database
    df.to_sql(con = engine, name=tablename_d, if_exists='replace')




