## NBA All-Time Season Statisitcs Acquision
# - This code web scrapes data from basketball reference to create a database of all players statistics for all NBA seasons
# - For each NBA player, all season stats are concated into a dataFrame, which is then saved to a MySQL database

# - The output file considers the following features for each player:
#   * Basic box-score stats
#   * Advanced box-score stats
#   * Year and team of the season

# - This method (while time consuming) obtains a relatively complete record of players and their statistics.

# Import Packages
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
from alive_progress import alive_bar
import string
import re
import requests
import pandas as pd


# MySQL Credentials
hostname = "localhost"
uname = "root"
pwd = "rootroot"
dbname = "nba_statistics"

# Inputs
table_name_pl = 'nba_players_db'
table_name_ac = 'nba_accolades_db'


# Initialize DataFrame
df = pd.DataFrame()
j = 0

# Obtain data for all nba players from basketball-reference.com
with alive_bar(5023, force_tty=True) as bar: # Initialize progress bar for individual teams
    for i, let in enumerate(string.ascii_lowercase): # Iterate over all players for all alphabetical letters
        # Obtain data from the player index on basketball reference
        url = 'https://www.basketball-reference.com/players/' + let + '/' # URL for player index on bball reference (by first letter of last name)
        data = requests.get(url).text
        soup = bs(data, "html.parser")
        table = soup.find('table')

        # Use beautiful soup to get the hyperlinks in team index table:
        links = []
        for tr in table.findAll("tr"):
            for each in tr:
                try:
                    link = each.find('a')['href']
                    if '/players/' in link:
                        links.append(link)
                except:
                    pass


        for link in links:  # Iterate over each player per alphabetical letter
            bar()  # Update progress bar
            url_yr = 'https://www.basketball-reference.com' + link
            data = pd.read_html(url_yr)

            # Obtain player name and birthyear:
            data_all = requests.get(url_yr).text
            soup = bs(data_all, "html.parser")
            player_name = soup.find('strong').contents[0].strip()
            for span in soup.findAll("span"):
                for each in span:
                    try:
                        if 'birthyears' in str(each):
                            birthyear  = int(str(each)[-8:-4])
                    except:
                        pass
            # Obtain all career accolades:
            champ = 0
            mvp = 0
            fmvp = 0
            allnba = 0
            alldef = 0
            allstar = 0
            hof = 0
            k = 0
            for a in soup.findAll("a"):
                for each in a:
                    try:
                        # Check for Hall of Fame Selection
                        if 'Hall of Fame' in each:
                            k = k+1
                            if k > 1:
                                hof = 1
                        # Check for NBA and ABA championships
                        if 'NBA Champ' in each:
                            if 'x' in each:
                                champ = champ + int(str(each)[0:2].replace('x',''))
                            else:
                                champ = champ + 1
                        if 'ABA Champ' in each:
                            if 'x' in each:
                                champ = champ + int(str(each)[0:2].replace('x',''))
                            else:
                                champ = champ + 1
                        # Check for All-NBA Selections:
                        if ' All-NBA' in each:
                            if 'x' in each:
                                allnba = allnba + int(str(each)[0:2].replace('x', ''))
                            else:
                                allnba = allnba + 1
                        # Check for All-Defensive Selections
                        if 'All-Defensive' in each:
                            if 'x' in each:
                                alldef = alldef + int(str(each)[0:2].replace('x', ''))
                            else:
                                alldef = alldef + 1
                        # Check for All-Star Selections
                        if 'All Star' in each:
                            if 'x' in each:
                                allstar = allstar + int(str(each)[0:2].replace('x', ''))
                            else:
                                allstar = allstar + 1
                        # Check for MVP and Finals MVP:
                        if 'MVP' in each:
                            if each == 'NBA MVP':
                                pass
                            else:
                                if 'Finals' in each:
                                    if 'x' in each:
                                        fmvp = fmvp + int(str(each)[0:2].replace('x', ''))
                                    else:
                                        fmvp = fmvp + 1
                                else:
                                    if 'AS' in each:
                                        pass
                                    else:
                                        if 'x' in each:
                                            mvp = mvp + int(str(each)[0:2].replace('x', ''))
                                        else:
                                            mvp = mvp + 1
                    except:
                        pass

            # Save accolades to a separate DataFrame
            if j == 0:
                accolades = pd.DataFrame([[player_name, birthyear, champ,mvp, fmvp, allstar, allnba, alldef, hof]])
                accolades.columns = ['player_name','birth_year','champ','mvp','fmvp','allstar','allnba','alldef', 'hof']
            else:
                accolades= pd.concat([accolades,pd.DataFrame([[player_name, birthyear, champ,mvp, fmvp, allstar, allnba, alldef, hof]], columns = ['player_name','birth_year','champ','mvp','fmvp','allstar','allnba','alldef', 'hof'])], axis = 0)
            j=j+1
            #print(player_name, 'champ: ', champ, 'mvp: ', mvp, 'fmvp: ', fmvp, 'allstar: ', allstar, 'allnba: ', allnba, 'alldef: ', alldef, 'hof: ', hof)

            # Obtain player Stats
            if len(data) == 6: # For players with playoff appearances
                df_year = data[2]
                df_year.drop(index = df_year.index[df_year.Tm == 'TOT'], inplace = True)
                df_year.drop(index=df_year.index[df_year.Age.isnull()], inplace=True)
                df_adv = data[4]
                df_adv.drop(index=df_adv.index[df_adv.Tm == 'TOT'], inplace=True)
                df_adv.drop(index=df_adv.index[df_adv.Age.isnull()], inplace=True)

            if len(data) == 3:  # For players without playoff experience:
                df_year = data[1]
                df_year.drop(index=df_year.index[df_year.Tm == 'TOT'], inplace=True)
                df_year.drop(index=df_year.index[df_year.Age.isnull()], inplace=True)
                df_adv = data[2]
                df_adv.drop(index=df_adv.index[df_adv.Tm == 'TOT'], inplace=True)
                df_adv.drop(index=df_adv.index[df_adv.Age.isnull()], inplace=True)

            # Concatenate traditional and advanced stats
            if 'BPM' in df_adv.columns:
                df_year[['OWS', 'DWS', 'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']] = df_adv[
                     ['OWS', 'DWS', 'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']]
            else:
                df_year[['OWS', 'DWS', 'WS', 'WS/48']] = df_adv[
                    ['OWS', 'DWS', 'WS', 'WS/48']]
                df_year[['OBPM', 'DBPM', 'BPM', 'VORP']] = None

            df_year[['PLAYER_NAME']] = player_name
            df_year[['BIRTH_YEAR']] = birthyear
            df = pd.concat([df, df_year], axis=0) # Concatenate player data with total df.

# Prepare DataFrame for saving
# Convert Season values to integers
seasons = df['Season'].values[:]
seasons = [int(x[:-3]) + 1 for x in seasons]
df['Season'] = seasons

# Reorder columns:
df = df[['PLAYER_NAME','BIRTH_YEAR','Season', 'Age', 'Tm', 'Lg', 'Pos', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%',
       '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
       'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'OWS',
       'DWS', 'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']]

# Save the DataFrame to a MySQL database
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
df.to_sql(con = engine, name=table_name_pl, if_exists='replace')
accolades.to_sql(con = engine, name=table_name_ac, if_exists='replace')




