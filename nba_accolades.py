## NBA Teams Data Acquision
# Code which uses NBA_API as well as webscrapping to obtain up-to-date NBA career accolades
# The output file adds the following features to the features from the NBA_seasons_db:
#   * MVP Shares, All-star, All-NBA selections
#   * Whether or not each player is active and if they are in the HOF
# The constructed dataframe is saved as a table in a MySQL database.

# Import Packages
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
from alive_progress import alive_bar
import numpy as np
import pyautogui
import requests
import pandas as pd

# Inputs:
tablename_d = 'nba_accolades_db' # Desination table

# MySQL Credentials
hostname = "localhost"
uname = "root"
pwd = "Sara!091996"
dbname = "nba_statistics"
tablename_s = 'nba_seasons_db' # Source table


# Import nba_seasons_db data from the database:
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
query = 'select player_name, max(season), sum(G), sum(GS), sum(MP), sum(FG), sum(FGA), sum(3P), sum(3PA), sum(2P), sum(2PA),' \
        'sum(FT), sum(FTA), sum(ORB), sum(DRB), sum(TRB), sum(AST), sum(STL),sum(BLK), sum(TOV), sum(PF), sum(PTS), sum(OWS),'\
        'sum(DWS), SUM(WS), sum(OBPM), sum(DBPM), sum(BPM) from %s group by player_name' % tablename_s # Query to obtain the desired data from the database.
df = pd.read_sql(sql = query, con = engine)
df.columns = ['player_name', 'last_played', 'G', 'GS', 'MP', 'FG', 'FGA', '3P', '3PA', '2P', '2PA', 'FT', 'FTA', 'ORB',
              'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'OWS', 'DWS', 'WS', 'OBPM', 'DBPM', 'BPM'] # Rename the columns of the dataFrame

with alive_bar(4, force_tty=True) as bar: # Initialize progress bar
    # Use Beautiful Soup and pd.read_html to webscrape additional stats such as Win Shares, All-Star Selections, All-NBA Selections, MVP Shares, and HOF Inductees
    # All-Star Selections
    bar() # Update progress bar
    df[['allstar']] = 0 # Create column for # of all-star selections
    url_as = 'https://www.basketball-reference.com/awards/all_star_by_player.html' # URL for All-star selections
    data = requests.get(url_as).text
    soup = bs(data, "html.parser")
    html_tables = soup.find_all('table')
    allstar = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
    # Merge the webscrapped data with the dataframe.
    for i, x in enumerate(allstar['Player']):
        df.loc[df['player_name'] == x, 'allstar'] = int(allstar.loc[i,'Tot'])


    # All-NBA Selections
    bar() # Update progress bar
    df[['allnba']] = 0 # Create column for # of all-nba selections
    url_allnba = 'https://www.basketball-reference.com/awards/all_league_by_player.html' # URL for All-NBA selections
    data = requests.get(url_allnba).text
    soup = bs(data, "html.parser")
    html_tables = soup.find_all('table')
    allnba = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
    allnba.columns = ['Rk', 'Player', 'Tot','1st','2nd','3rd','TotNBA','1ABA','2ABA','TotABA']
    # Merge the webscrapped data with the dataframe.
    for i, x in enumerate(allnba['Player']):
        df.loc[df['player_name'] == x, 'allnba'] = int(allnba.loc[i,'Tot'])

    # MVP Shares
    bar() # Update progress bar
    df[['mvp']] = 0 # Create column for # of all-nba selections
    url = 'https://www.basketball-reference.com/leaders/nba_mvp_shares.html' # URL for MVP shares
    data = requests.get(url).text
    soup = bs(data, "html.parser")
    html_tables = soup.find_all('table')
    mvpshares = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
    mvpshares['Player'] = mvpshares['Player'].str.replace('*','', regex = True)
    # Merge the webscrapped data with the dataframe.
    for i, x in enumerate(mvpshares['Player']):
        df.loc[df['player_name'] == x, 'mvp'] = mvpshares.loc[i,'MVP Shares']

    # Labelling the HOF inductees
    bar() # Update progress bar
    df[['hof']] = 0 # Create column for # of all-nba selections
    url = 'https://en.wikipedia.org/wiki/List_of_players_in_the_Naismith_Memorial_Basketball_Hall_of_Fame' # URL for HOF inductees
    data = requests.get(url).text
    soup = bs(data, "html.parser")
    html_tables = soup.find_all('table')
    hof = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
    hof['Inductees'] = hof['Inductees'].str.replace('*','', regex = True)
    # Merge the webscrapped data with the dataframe.
    for i, x in enumerate(hof['Inductees']):
        df.loc[df['player_name'] == x, 'hof'] = 1

# Data cleansing: Fixing missing values in the database
# Drop players who are missing basic stats:
df = df.drop(axis = 0, index = df.index[pd.isna(df.TRB)]).reset_index()

# Missing values of ORB and DRB
oreb_ratio = np.asarray(df.ORB.drop(axis = 0, index = df.index[df.TRB == 0]))/np.asarray(df.TRB.drop(axis = 0, index = df.index[df.TRB == 0])) # Obtain the average ratio of ORB to TRB
oreb_ratio= oreb_ratio[~pd.isna(oreb_ratio)]
oreb_ratio = np.average(oreb_ratio)

for i, x in enumerate(df.ORB): # Replace Nan values with the player's total TRB times the average ORB/TRB ratio
    if pd.isna(x):
        df.loc[i,'ORB'] = int(df.loc[i,'TRB']*oreb_ratio)

for i, x in enumerate(df.DRB): # Replace Nan values with the player's total TRB times the average DRB/TRB ratio
    if pd.isna(x):
        df.loc[i,'DRB'] = int(df.loc[i,'TRB']*(1-oreb_ratio))

# Missing values of STL and BLK
df['BLK'].fillna(value = np.average(df.BLK.dropna()), inplace = True) # Replace BLK Nan values with the average BLK value
df['STL'].fillna(value = np.average(df.STL.dropna()), inplace = True) # Replace STL Nan values with the average STL value

# Print the DataFrame.
#print(df.sort_values('PTS',ascending= False)[df.columns])
print(df[['player_name','WS','TRB','ORB','DRB']].sort_values('TRB',ascending= False).head(10))
print(df.columns)

# Create dialog box to confirm the saving of the file
conf = pyautogui.confirm('Save Dataframe to file?')

# Save the DataFrame to file.
if conf == 'OK':
    # Save the DataFrame to a MySQL database
    engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
    df.to_sql(con = engine, name=tablename_d, if_exists='replace')
