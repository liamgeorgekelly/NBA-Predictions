## NBA Data Acquision
# Code which uses NBA_API as well as webscrapping to obtain up-to-date NBA statistics. Webscrapped websites are basketballreference and wikipedia.
# The output file considers the following features:
#   * PTS, AST, REB, OREB, DREB, BLK, STL (Total, Career, Regular Season)
#   * MVP Shares, Win Shares
#   * All-star, All-NBA selections
#   * Whether or not each player is active and if they are in the HOF
# The constructed dataframe is saved locally as a .csv file.

# Inputs:
file_name = 'df_players'
file_path = 'C:\\Users\\liamg\\PycharmProjects\\NBApredictions\\data\\'

# Import Packages
from nba_api.stats.endpoints import alltimeleadersgrids
from nba_api.stats.static import players
from bs4 import BeautifulSoup as bs
import pyautogui
import requests
import pandas as pd

# Use NBA_API to acquire career total box score statistics (regular season):


leaders_totals = alltimeleadersgrids.AllTimeLeadersGrids(topx = 5000)  # Request box score statistics from the API
# Import stats from the API into the dataframe (df):
df = leaders_totals.pts_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['PLAYER_NAME','PTS']]
df[['AST']] = leaders_totals.ast_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['AST']]
df[['DREB']] = leaders_totals.dreb_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['DREB']]
df[['OREB']] = leaders_totals.oreb_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['OREB']]
df[['REB']] = leaders_totals.reb_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['REB']]
df[['BLK']] = leaders_totals.blk_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['BLK']]
df[['STL']] = leaders_totals.stl_leaders.get_data_frame().sort_values('PLAYER_ID').reset_index(drop=True)[['STL']]

# Add additional column to label which players are actively playing in the NBA.
df[['ACTIVE?']] = 0
df_active = pd.DataFrame(players.get_players()).sort_values('id').reset_index(drop=True)[['full_name','is_active']] # Request player info from the API
df_active = df_active[df_active.is_active == True]
for x in df_active.full_name:
    df.loc[df.index[df.PLAYER_NAME == x],'ACTIVE?'] = 1

# Use Beautiful Soup and pd.read_html to webscrape additional stats such as Win Shares, All-Star Selections, All-NBA Selections, MVP Shares, and HOF Inductees

# Win Shares
df[['WS']] = 0 # Initialize column for win-shares (players with no win-share data will have a value of 0).
url_ws = 'https://www.basketball-reference.com/leaders/ws_career.html' # URL for win shares
data = requests.get(url_ws).text
soup = bs(data, "html.parser")
html_tables = soup.find_all('table')
winshares = pd.read_html(str(html_tables), flavor = 'bs4')[0] # Create pd.Dataframe from the html data
winshares['Player'] = winshares['Player'].str.replace('*','', regex = True)
# Merge the webscrapped data with the dataframe.
for i, x in enumerate(winshares['Player']):
    df.loc[df['PLAYER_NAME'] == x, 'WS'] = winshares.loc[i,'WS']

# All-Star Selections
df[['ALLSTAR']] = 0 # Create column for # of all-star selections
url_as = 'https://www.basketball-reference.com/awards/all_star_by_player.html' # URL for All-star selections
data = requests.get(url_as).text
soup = bs(data, "html.parser")
html_tables = soup.find_all('table')
allstar = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
# Merge the webscrapped data with the dataframe.
for i, x in enumerate(allstar['Player']):
    df.loc[df['PLAYER_NAME'] == x, 'ALLSTAR'] = int(allstar.loc[i,'Tot'])


# All-NBA Selections
df[['ALLNBA']] = 0 # Create column for # of all-nba selections
url_allnba = 'https://www.basketball-reference.com/awards/all_league_by_player.html' # URL for All-NBA selections
data = requests.get(url_allnba).text
soup = bs(data, "html.parser")
html_tables = soup.find_all('table')
allnba = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
allnba.columns = ['Rk', 'Player', 'Tot','1st','2nd','3rd','TotNBA','1ABA','2ABA','TotABA']
# Merge the webscrapped data with the dataframe.
for i, x in enumerate(allnba['Player']):
    df.loc[df['PLAYER_NAME'] == x, 'ALLNBA'] = int(allnba.loc[i,'Tot'])

# MVP Shares
df[['MVP']] = 0 # Create column for # of all-nba selections
url = 'https://www.basketball-reference.com/leaders/nba_mvp_shares.html' # URL for MVP shares
data = requests.get(url).text
soup = bs(data, "html.parser")
html_tables = soup.find_all('table')
mvpshares = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
mvpshares['Player'] = mvpshares['Player'].str.replace('*','', regex = True)
# Merge the webscrapped data with the dataframe.
for i, x in enumerate(mvpshares['Player']):
    df.loc[df['PLAYER_NAME'] == x, 'MVP'] = mvpshares.loc[i,'MVP Shares']

# Labelling the HOF inductees
df[['HOF']] = 0 # Create column for # of all-nba selections
url = 'https://en.wikipedia.org/wiki/List_of_players_in_the_Naismith_Memorial_Basketball_Hall_of_Fame' # URL for HOF inductees
data = requests.get(url).text
soup = bs(data, "html.parser")
html_tables = soup.find_all('table')
hof = pd.read_html(str(html_tables), flavor = 'bs4')[0]  # Create pd.Dataframe from the html data
hof['Inductees'] = hof['Inductees'].str.replace('*','', regex = True)
# Merge the webscrapped data with the dataframe.
for i, x in enumerate(hof['Inductees']):
    df.loc[df['PLAYER_NAME'] == x, 'HOF'] = 1

# Print the DataFrame.
print(df.sort_values('PTS',ascending= False)[df.columns])
print(df.columns)
# Create dialog box to confirm the saving of the file
conf = pyautogui.confirm('Save Dataframe to file?')

# Save the DataFrame to file.
if conf == 'OK':
    df.to_csv(file_path + file_name + '.csv')





