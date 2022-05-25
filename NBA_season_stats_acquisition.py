## NBA All-Time Season Statisitcs Acquision
# - This code web scrapes data from basketball reference to create a database of all players statistics for all NBA seasons
# - For each NBA team, the data from each season is scraped and concated into a dataFrame, which is then saved to a MySQL database

# - The output file considers the following features for each player:
#   * Basic box-score stats
#   * Advanced box-score stats
#   * Year and team of the season

# - This method (while time consuming) obtains a relatively complete record of players and their statistics.

# Import Packages
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
from alive_progress import alive_bar
import requests
import pandas as pd


# MySQL Credentials
hostname = "localhost"
uname = "root"
pwd = "Sara!091996"
dbname = "nba_statistics"

# Inputs
file_name = 'nba_seasons_db'
all_teams = 1 # Switch to determine if all teams will be web scraped. 1 = all teams, 0 = only specified teams.
teams = ['ATL', 'NJN', 'BOS',	'CHA',	'CHI',	'CLE',	'DAL',	'DEN',	'DET',	'GSW',	'HOU',	'IND',
         'LAC',	'LAL',	'MEM', 'MIA',	'MIL',	'MIN',	'NOH',	'NYK',	'OKC',	'ORL',	'PHI',	'PHO',	'POR',
         'SAC',	'SAS',  'TOR',	'UTA', 'WAS'] # Teams that will be added to the database if all_teams = 0


# Initialize DataFrame
df = pd.DataFrame()

# Obtain all team abbreviations if all_teams = 1:
if all_teams == 1:
    url = 'https://www.basketball-reference.com/teams/' # URL for all teams
    data = requests.get(url).text
    soup = bs(data, "html.parser")
    table = soup.findAll('table')
    teams = []
    for i in range(len(table)):
        for tr in table[i].findAll("tr"):
            for each in tr:
                try:
                    link = each.find('a')['href']
                    teams.append(link[len(link)-4:len(link)-1])
                except:
                    pass


with alive_bar(len(teams), force_tty=True) as bar: # Initialize progress bar

# Iterate over all seasons for each NBA team
    for team_name in teams:
        bar() # Update progress bar

        url = 'https://www.basketball-reference.com/teams/' + team_name + '/' # URL for team index on bball reference
        data = requests.get(url).text
        soup = bs(data, "html.parser")
        table = soup.find('table')

        # Use beautiful soup to get the hyperlinks
        links = []
        for tr in table.findAll("tr"):
            trs = tr.findAll("td")
            for each in trs:
                try:
                    link = each.find('a')['href']
                    if '/teams/' in link:
                        links.append(link)
                except:
                    pass

        for link in links:
            url_yr = 'https://www.basketball-reference.com' + link
            if len(pd.read_html(url_yr)) == 7:
                df_year = pd.read_html(url_yr)[1].sort_values('Unnamed: 1').reset_index()
                df_adv = pd.read_html(url_yr)[5].sort_values('Unnamed: 1').reset_index()
            else:
                df_year = pd.read_html(url_yr)[1].sort_values('Unnamed: 1').reset_index()
                df_adv = pd.read_html(url_yr)[3].sort_values('Unnamed: 1').reset_index()
            df_year.drop(axis=1, labels = ['Rk','index'], inplace = True)
            df_year[['OWS','DWS','WS','WS/48','OBPM','DBPM','BPM']] = df_adv[['OWS','DWS','WS','WS/48','OBPM','DBPM','BPM']]
            df_year[['team']] = team_name
            df_year[['season']] = int(link[len(link)-9:len(link)-5])
            df = pd.concat([df,df_year],axis = 0)

# Prepare DataFrame for saving
df.reset_index(inplace = True)
df.drop(axis=1, labels = ['index'], inplace = True) # Reset and drop the index

df.columns = ['player_name', 'age', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
             '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB',
             'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS/G', 'OWS', 'DWS', 'WS',
             'WS/48', 'OBPM', 'DBPM', 'BPM', 'team', 'season'] # Rename df columns

print(df.columns)
df = df[['player_name', 'age', 'team', 'season', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
             '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB',
             'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS/G', 'OWS', 'DWS', 'WS',
             'WS/48', 'OBPM', 'DBPM', 'BPM']] # Rearrange columsn in the datafram

# Save the DataFrame to a MySQL database
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
df.to_sql(con = engine, name=file_name, if_exists='replace')



