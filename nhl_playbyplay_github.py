# -*- coding: utf-8 -*-
"""nhl_playbyplay_github.ipynb

Automatically generated by Colaboratory.

The goal of this python project is to take the data available in this [link](hhttps://www.kaggle.com/martinellis/nhl-game-data) , process it and create some features in a way that can be visualized in Tableau, allowing x,y point shot analysis with NHL Hockey data.

A background image that helps a lot when plotting is available [here](https://www.kaggle.com/kapastor/nhl-analysis-shot-distribution/comments#808618).

# **SETUP**
"""

# Commented out IPython magic to ensure Python compatibility.
# pandas para manipulação de dataframes
import pandas as pd

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# pacotes de visualização de dados
import matplotlib.pyplot as plt
from matplotlib import cm
# %matplotlib inline
import seaborn as sns; sns.set()

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# pacotes para estatísticas e criação de modelos
import numpy as np
from scipy import stats

# CLUSTER
from sklearn.cluster import KMeans

# PCA 
from sklearn.decomposition import PCA
# Import the KElbowVisualizer method 
from yellowbrick.cluster import KElbowVisualizer

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# upload de arquivos 
from google.colab import files

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

# Configurando o número máximo de linhas a se mostrar
pd.set_option('display.max_row', 5000)

# Configurando o número máximo de colunas a se mostrar
pd.set_option('display.max_columns', 50)

# Aumentando o número de caracteres a serem exibidos numa coluna de texto
pd.options.display.max_colwidth = 500

# Desligando a notificação setcopywarning - Já contolamos a situação
pd.set_option('mode.chained_assignment', None)

uploaded = files.upload()

"""# **Reading and showing the dataframe**"""

df0 = pd.read_csv('game_plays.csv', encoding = 'unicode_escape', error_bad_lines=False, sep=',')
type(df0)
df0.head(5)

"""# **Converting dateTime to datetime format and calculating between rows difference in time with Diff**"""

# checking variable type
df0['dateTime'].dtype

# converting the variable from text to datetime
df0['dateTime']= pd.to_datetime(df0['dateTime']) 

# checking variable type to see if it really changed
df0['dateTime'].dtype

# sorting the dataframe by game_id (game) and play_num ascending
df1 = df0.sort_values(["game_id", "play_num"], ascending = (True, True))

# calculating the difference, in seconds, from the current play (row) to the previous
df1['diff_evento'] = df1['periodTime'].diff()

# df1['event'].value_counts()
# df.fillna({'sex':-1}, inplace=True)
# pd.crosstab(df1.secondaryType, df1.event)

df1.head(5)

"""# **Exploring data to see the general pattern that the plays are reported**

### **Blocked Shots**
"""

# creating the mask to be applied in the dataframe filtering
is_2002 =  df1['event']=='Blocked Shot'

# filtering the dataframe to only contain Blocked Shots records
df2 = df1[is_2002]

# checking the results
df2.head(5)

# performing a frequency count 
df2['description'].value_counts()

# EXAMPLE OF PATTERN ANALYSIS:
# IF I WANT TO IDENTIFY WHO BLOCKED THE SHOTS AND WHO WAS BLOCKED, BREAKING THE RECORD INTO TWO COLUMNS:
# IDENTIFY  "blocked shot from" and replace it as a special string, like "@"
# OPERATE OVER THE REMAINING STRING, PARTITIONING IT OVER THAT SYMBOL (BEFORE / AFTER) TO SEPARATE INTO COLUMNS

"""### **Takeaways**"""

is_2002 =  df1['event']=='Takeaway'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

"""### **Goals**"""

is_2002 =  df1['event']=='Goal'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

"""### **Shots**"""

is_2002 =  df1['event']=='Shot'
df2 = df1[is_2002]
df2.head(5)

# df2['description'].value_counts()

"""### **Penalties**"""

is_2002 =  df1['event']=='Penalty'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

"""### **Faceoffs**"""

is_2002 =  df1['event']=='Faceoff'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

"""### **Stoppage**"""

is_2002 =  df1['event']=='Stoppage'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

"""### **Hit**"""

is_2002 =  df1['event']=='Hit'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

"""### **Missed Shots**"""

is_2002 =  df1['event']=='Missed Shot'
df2 = df1[is_2002]
df2.head(5)
#df2['description'].value_counts()

events = ['Shot', 'Goal']

# actually filtering the dataframe
df1000= df1[df1.event.isin(events)]
df1000.describe()
df1000.to_csv("C:\musical_data\shots_goals.csv" , sep=';' )

"""## **SHOT ANALYSIS DATABASE CREATION**

Since we have analyzed all types of plays patterns´s, I have decided to study shots as a whole, ie. missed and blocked shots, goals and shots saved by goalies. So in the next sections we create the intermediate and final columns necessary to finish the database.

***Blocked Shots***
"""

# We have to include the Period Start event, to avoid high negative difference numbers between shots that may occur when we have a new period.
# It´s a good exercise to check via a histogram how the distribution changes, as they are almost 10k rows in our database.
#'Shot', 'Blocked Shot', 'Missed Shot',

#events = ['Blocked Shot']
#df2= df1[df1.event.isin(events)]

# types of shots that I want to filter
events = ['Shot', 'Blocked Shot', 'Missed Shot', 'Goal', 'Period Start']

# actually filtering the dataframe
df2= df1[df1.event.isin(events)]
df2.head(5)

# identifying the pattern to split the record, replacing it by "@" 
# and creating a new temporary column called description2:
df2["description2"]= df2["description"].str.replace(' blocked shot from ', '@')
df2.head(10)

# Taking the name of the "other player", ie, tha player that blocked 
# the shot and assigning it to the "OTHER_PLAYER_BLOCK" column as a 
# result of the partition "0" (before the @) extraction:

df2['other_player_block'] = df2['description2'].str.split('@').str[0]

# As I already have in mind that I will have to do some column merging 
# at the end of the whole process, if a play is not Blocked Shot in 
# "EVENT" column, I assign an empty value to the row in the 
# "OTHER PLAY BLOCK" column wich, in effect, will leave filled only the 
# records that interests to the blocked shot statistic.

#  { COL. "OTHER_PLAYER_BLOCK" UNTIL NOW } -----------------------------  { COL. "OTHER_PLAYER_BLOCK" AFTER NEXT STEP: }
#                       |                                                                      |                   
# | EVENT        | OTHER_PLAYER_BLOCK  ===---------------------------===> | EVENT        | OTHER_PLAYER_BLOCK
# | goal         | Jarome Iginla       ===                           ===> | goal         | 
# | missed shot  | Sidney Crosby       ===                           ===> | missed shot  | 
# | missed shot  | Alex Ovechkin       === APPLYING CORRECTION BELOW ===> | missed shot  | 
# | blocked shot | Brian Dumolin       ===                           ===> | blocked shot | Brian Dumolin
# | shot         | Brian Gionta        ===                           ===> | shot         | 
# | blocked shot | Aaron Ekblad        ===---------------------------===> | blocked shot | Aaron Ekblad

df2.loc[df2['event'] != "Blocked Shot" , 'other_player_block'] = ''
df2.loc[df2['event'] == "Blocked Shot" , 'shot_blocked'] = 'Blocked Shot'
df2.head(10)

# Now, taking the name of the player whose shot WAS BLOCKED into column 
# "OTHER_PLAYER_BLOCK"as a result of the partition "1" (after the @) extraction:

df2['player_miss_block'] = df2['description2'].str.split('@').str[1]

# Again, the same operation cleaning the rows of PLAYER_MISS_BLOCK when
# the value in the column "EVENT" is not BLOCKED SHOT:

df2.loc[df2['event'] != "Blocked Shot" , 'player_miss_block'] = ''
df2.head(5)

"""***Missed Shots***"""

#'Shot', 'Blocked Shot', 'Missed Shot',

#events = ['Sidney Crosby - Wide of Net']
#df2= df1[df1.description.isin(events)]

#events = ['Sidney Crosby - Wide of Net','Sidney Crosby - Over Net','Sidney Crosby - Hit Crossbar','Sidney Crosby - Goalpost']
#df2= df1[df1.description.isin(events)]

#events = ['Shot', 'Blocked Shot', 'Missed Shot', 'Goal']
#df2= df1[df1.event.isin(events)]

# The same general logic applies to the MISSED SHOTS, but the approach needs to be
# a little different, because we have 4 types of missed shots so we have 4 different
# patterns that have to be identified: wide of net, over net, crossbar and goalpost.

#MISSED SHOTS

df2["miss_wide"]= df2["description"].str.replace(' - Wide of Net', '@wideofnet')
df2["miss_over"]= df2["description"].str.replace(' - Over Net', '@overnet')
df2["miss_cross"]= df2["description"].str.replace(' - Hit Crossbar', '@crossbar')
df2["miss_post"]= df2["description"].str.replace(' - Goalpost', '@goalpost')
df2.head(4)

#MISSED SHOTS - WIDE OF NET
# Instead of two player name columns, here we have just one, PLAYER_MISS_WIDE
# So I take the name of the player who missed the shot as usual, extracting the 
# portion before the "@"

df2['player_miss_wide'] = df2['miss_wide'].str.split('@').str[0]

# and then I follow identifying if the portion after the "@" is wideofnet. If it
# is not, then I clear the record stored in MISS_WIDE, as I made before for the
# blocked shots. It´s a bit different, but as I said, the general logic applies:

df2.loc[df2['miss_wide'].str.split('@').str[1] != "wideofnet" , 'player_miss_wide'] = ''
df2.head(10)

# VALIDATION
# df2['player_miss_wide'].value_counts()

# I also create MISS_TYPE_WIDE to record the type of missed shot: 
# Extraction the part after the "@"

df2['miss_type_wide'] = df2['miss_wide'].str.split('@').str[1]

# Checking if the resulting string is "wideofnet". If true, assign "Wide of Net"
# to the MISS_TYPE_WIDE column

df2.loc[df2['miss_type_wide'] == "wideofnet" , 'miss_type_wide'] = "Wide of Net"

# VALIDATION
# df2.head(10)
# df2['miss_type_wide'].value_counts()

# The process goes on, just changing the miss type and the variables names...

#MISSED SHOTS - OVER NET
# Pegando o nome do jogador que errou:
df2['player_miss_over'] = df2['miss_over'].str.split('@').str[0]
df2.loc[df2['miss_over'].str.split('@').str[1] != "overnet" , 'player_miss_over'] = ''
df2.head(4)
df2['player_miss_over'].value_counts()

# e neste caso, também temos interesse no tipo de miss
df2['miss_type_over'] = df2['miss_over'].str.split('@').str[1]
df2.loc[df2['miss_type_over'] == "overnet" , 'miss_type_over'] = "Over Net"
df2.head(4)
df2['miss_type_over'].value_counts()

#MISSED SHOTS - CROSSBAR
# Pegando o nome do jogador que errou:
df2['player_miss_cross'] = df2['miss_cross'].str.split('@').str[0]
df2.loc[df2['miss_cross'].str.split('@').str[1] != "crossbar" , 'player_miss_cross'] = ''
df2.head(4)
df2['player_miss_cross'].value_counts()

# e neste caso, também temos interesse no tipo de miss
df2['miss_type_cross'] = df2['miss_cross'].str.split('@').str[1]
df2.loc[df2['miss_type_cross'] == "crossbar" , 'miss_type_cross'] = "Hit Crossbar"
df2.head(4)
df2['miss_type_cross'].value_counts()

#MISSED SHOTS - GOAL POST
# Pegando o nome do jogador que errou:
df2['player_miss_post'] = df2['miss_post'].str.split('@').str[0]
df2.loc[df2['miss_post'].str.split('@').str[1] != "goalpost" , 'player_miss_post'] = ''
df2.head(4)
df2['player_miss_post'].value_counts()

# e neste caso, também temos interesse no tipo de miss
df2['miss_type_post'] = df2['miss_post'].str.split('@').str[1]
df2.loc[df2['miss_type_post'] == "goalpost" , 'miss_type_post'] = "Goalpost"
df2.head(5)

"""***Goals***"""

#GOALS
#Com regex, vamos identificar as duas formas de atribuição de gols no Play by Play, que é com os gols realizados entre parenteses (regular season) e com traço separando do tipo de tacada no SHOOTOUT
import re
df2["player_temp"]=  df2['description'].str.replace(r'\((\d+)\)', '@', regex=True)
df2["player_temp2"]=  df2['player_temp'].str.replace(r'(\s-\s)', '@', regex=True)

# Aí, extraímos o nome do jogador, independente de qual seja e qual caracter especial tenha, identificando-o antes do @
# os nomes dos jogadores podem estar separados pelo nosso @ ou pelo traço (nesse caso virá pelo campo description)
# COALESCE, SE PRECISAR >> #df2['player_goal'] = df2.player_goal1.combine_first(df2.player_goal2)
df2['player_goal'] = df2['player_temp2'].str.split('@').str[0]
df2.loc[df2["event"].str.strip()!="Goal", "player_goal"] = ''

# goal shot type
df2.loc[df2["player_goal"].str.strip()!="", "goal_shot_type"] = df2["secondaryType"]
df2.head(5)

#df2['player_goal'].value_counts()

"""***Shots***"""

#SHOTS
# Aqui a situação é um pouco diferente porque o tipo de tacada também conta depois do nome do jogador, então vamos utilizar translate com um dicionário para fazer todas as modificações de uma vez

dict2 = {" Backhand saved by ":"@", " Slap Shot saved by ":"@", " Snap Shot saved by ":"@", " Tip-In saved by ":"@", " Wrap-around saved by ":"@", " Wrist Shot saved by ":"@", " Deflected saved by ":"@"}
df2["playershot_temp"]= df2["description"].replace(dict2, regex=True)
df2

# Aí, extraímos o nome do jogador, independente de qual seja e qual caracter especial tenha, identificando-o antes do @
# os nomes dos jogadores podem estar separados pelo nosso @ ou pelo traço (nesse caso virá pelo campo description)
# COALESCE, SE PRECISAR >> #df2['player_goal'] = df2.player_goal1.combine_first(df2.player_goal2)
df2['player_shot'] = df2['playershot_temp'].str.split('@').str[0]
df2.loc[df2["event"].str.strip()!="Shot", "player_shot"] = ''
df2.head(5)
df2['player_shot'].value_counts()

# e neste caso, também temos interesse nos goleiros que fizeram as defesas
df2['saved_by'] = df2['playershot_temp'].str.split('@').str[1]
df2.loc[df2["event"].str.strip()!="Shot", "saved_by"] = ''

# goal shot type
df2.loc[df2["player_shot"].str.strip()!="", "shot_shot_type"] = df2["secondaryType"]

df2.head(5)
#df2['saved_by'].value_counts()

"""## **Coalesce and Temporary Columns Deletion**"""

# COALESCE, SE PRECISAR >> 

# concatenating player name variables
cols1 = ['player_miss_block', 'player_miss_wide', 'player_miss_over','player_miss_cross', 'player_miss_post', 'player_goal','player_shot']
df2['player_name0'] = df2[cols1].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
df2["player_name"]= df2["player_name0"].str.replace('_', '')

# concatenating other players variables, when available
cols2 = ['saved_by', 'other_player_block']
df2['other_player_name0'] = df2[cols2].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
df2["other_player_name"]= df2["other_player_name0"].str.replace('_', '').str.replace('nan', '')

# concatenating shot type variables
cols3 = ['shot_blocked', 'miss_type_wide', 'miss_type_over','miss_type_cross', 'miss_type_post','goal_shot_type','shot_shot_type']
df2['shot_type0'] = df2[cols3].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
df2["shot_type"]= df2["shot_type0"].str.replace('_', '').str.replace('nan', '')

df2['diff_shots'] = df2['periodTime'].diff()

df2.drop(['player_name0', 'player_miss_block', 'player_miss_wide', 'player_miss_over','player_miss_cross', 'player_miss_post', 'player_goal','player_shot',
         'miss_wide', 'miss_over','miss_cross', 'miss_post', 'player_name0', 'other_player_name0', 'shot_type0', 'playershot_temp', 'player_temp', 'player_temp2', 'description2',
          'other_player_block', 'shot_blocked', 'saved_by', 'miss_type_wide', 'miss_type_over', 'miss_type_cross', 'miss_type_post','goal_shot_type', 'shot_shot_type'], axis=1)

# validação


df3 = pd.DataFrame({
'game_id': df2.loc[:, 'game_id'], 
'play_num': df2.loc[:, 'play_num'],
'period': df2.loc[:, 'period'], 
'event': df2.loc[:, 'event'], 
'periodTime': df2.loc[:, 'periodTime'], 
'description': df2.loc[:, 'description'], 
'st_x': df2.loc[:, 'st_x'], 
'st_y': df2.loc[:, 'st_y'], 
'rink_side': df2.loc[:, 'rink_side'], 
'player_name': df2.loc[:, 'player_name'], 
'other_player_name': df2.loc[:, 'other_player_name'], 
'shot_type': df2.loc[:, 'shot_type'], 
'diff_shots': df2.loc[:, 'diff_shots'], 

})
#.combine_first(df2.player_miss_over).combine_first(df2.player_miss_cross).combine_first(df2.player_miss_post).combine_first(df2.player_goal).combine_first(df2.player_shot)
df3.head(50)

events = ['Shot', 'Blocked Shot', 'Missed Shot', 'Goal']

# actually filtering the dataframe
df4= df3[df3.event.isin(events)]
df4.head(5)

df4['diff_shots'].value_counts()

df5 = pd.DataFrame({
'date_time': df2.loc[:, 'dateTime'], 
'game_id': df2.loc[:, 'game_id'], 
'play_num': df2.loc[:, 'play_num'],
'period': df2.loc[:, 'period'], 
'team_id_for': df2.loc[:, 'team_id_for'], 
'team_id_against': df2.loc[:, 'team_id_against'], 
'event': df2.loc[:, 'event'], 
'periodTime': df2.loc[:, 'periodTime'], 
'description': df2.loc[:, 'description'], 
'X': df2.loc[:, 'x'], 
'Y': df2.loc[:, 'y'], 
'st_x': df2.loc[:, 'st_x'], 
'st_y': df2.loc[:, 'st_y'], 
'rink_side': df2.loc[:, 'rink_side'], 
'player_name': df2.loc[:, 'player_name'], 
'other_player_name': df2.loc[:, 'other_player_name'], 
'shot_type': df2.loc[:, 'shot_type'], 
'diff_shots': df2.loc[:, 'diff_shots'], 

})

df5.head(5)

"""# **Importing team_id lookup table**"""

uploaded = files.upload()

df_team = pd.read_csv('team_info.csv', encoding = 'unicode_escape', error_bad_lines=False, sep=',')
type(df_team)
df_team.head(5)

df_team_for     =  pd.read_csv('team_info.csv', encoding = 'unicode_escape', error_bad_lines=False, sep=',')
df_team_for.rename(columns={'team_id':'team_id_for','franchiseId':'franchiseId_for','shortName':'shortName_for','teamName':'teamName_for','abbreviation':'abbreviation_for'}, inplace=True)
df6 = pd.merge(df5, df_team_for, on='team_id_for', how='left')

df_team_against = pd.read_csv('team_info.csv', encoding = 'unicode_escape', error_bad_lines=False, sep=',')
df_team_against.rename(columns={'team_id':'team_id_against','franchiseId':'franchiseId_against','shortName':'shortName_against','teamName':'teamName_against','abbreviation':'abbreviation_against'}, inplace=True)
df77 = pd.merge(df6, df_team_against, on='team_id_against', how='left')

df77.head(5)

"""# **Importing game lookup table**"""

uploaded = files.upload()

df_game = pd.read_csv('game.csv', encoding = 'unicode_escape', error_bad_lines=False, sep=',')
type(df_game)
df_game.head(5)

df_game2 = df_game.drop(['date_time', 'outcome', 'home_rink_side_start', 'venue_link','venue_time_zone_id', 'venue_time_zone_offset', 'venue_time_zone_tz'], axis=1)
df_game2.head(5)

df75 = pd.merge(df77, df_game2, on='game_id', how='left')

df75.head(5)

# Bringing the names for home and away teams
df_team_b = df_team.drop(['franchiseId', 'link'], axis=1)
df_team_b.rename(columns={'shortName':'shortName_home','teamName':'teamName_home','abbreviation':'abbreviation_home'}, inplace=True)

df76 = pd.merge(df75, df_team_b, left_on=['home_team_id'], right_on=['team_id'], how='left')

df_team_b = df_team.drop(['franchiseId', 'link'], axis=1)
df_team_b.rename(columns={'shortName':'shortName_away','teamName':'teamName_away','abbreviation':'abbreviation_away'}, inplace=True)

df7 = pd.merge(df76, df_team_b, left_on=['away_team_id'], right_on=['team_id'], how='left')

df7.head(5)

# Import math Library
import math

df8 = pd.DataFrame({
'date_time': df7.loc[:, 'date_time'], 
'unique_game_play': df7['game_id'].astype(str)+' '+df7['play_num'].astype(str),
'game_id': df7.loc[:, 'game_id'], 
'play_num': df7.loc[:, 'play_num'],
'period': df7.loc[:, 'period'], 
'team_for': df7.loc[:, 'abbreviation_for'], 
'team_against': df7.loc[:, 'abbreviation_against'], 
'event': df7.loc[:, 'event'], 
'periodTime': df7.loc[:, 'periodTime'], 
'description': df7.loc[:, 'description'], 
'x': df7.loc[:, 'X'], 
'y': df7.loc[:, 'Y'], 
'st_x': df7.loc[:, 'st_x'], 
'st_y': df7.loc[:, 'st_y'], 
'rink_side': df7.loc[:, 'rink_side'], 
'player_name': df7.loc[:, 'player_name'], 
'other_player_name': df7.loc[:, 'other_player_name'], 
'shot_type': df7.loc[:, 'shot_type'], 
'diff_shots': df7.loc[:, 'diff_shots'], 
'team_name_for': df7['shortName_for']+' '+df7['teamName_for'],
'team_name_against': df7['shortName_against']+' '+df7['teamName_against'],
'team_name_home': df7['shortName_home']+' '+df7['teamName_home'],
'team_name_away': df7['shortName_away']+' '+df7['teamName_away'],
'abbrev_home': df7.loc[:, 'abbreviation_home'], 
'abbrev_away': df7.loc[:, 'abbreviation_away'], 
'away_goals': df7.loc[:, 'away_goals'], 
'home_goals': df7.loc[:, 'home_goals'], 
'venue': df7.loc[:, 'venue'],  
'distance': ( (89-df7.loc[:, 'st_x'])**2 + df7.loc[:, 'st_y']**2 ) ** (1/2),
'angle': np.arctan2(df7.loc[:, 'st_y'], 89-df7.loc[:, 'st_x']) * (180/math.pi),
'angle_abs': abs(np.arctan2(df7.loc[:, 'st_y'], 89-df7.loc[:, 'st_x']) * (180/math.pi))
})

# Getting rid of the Period Start Lines with negative differences
events = ['Shot', 'Blocked Shot', 'Missed Shot', 'Goal']

# actually filtering the dataframe
df9= df8[df8.event.isin(events)]
df9.head(5)

"""## **Further Categorizations**"""

# ===========================================================================================================
# Angle Binning from:
# http://hockeyanalytics.com/Research_files/SQ-RS0910-Krzywicki.pdf
# ===========================================================================================================

# PERIOD TIME FRAME -|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|

# Create a variable called period_time_bin with four bins
custom_bucket_array = np.linspace(0, 1200, 5)
df9['period_time_bin'] = pd.cut(df9['periodTime'], custom_bucket_array)
pd.value_counts(df9['period_time_bin'])

# Now, naming the intervals; must be unique names. 4 intervals
tfs = ["start", "middle1", "middle2", "end"]
df9['period_tf4'] = pd.cut(df9['periodTime'].astype(float), [   0.,  300.,  600.,  900., 1200.], labels=tfs)
pd.value_counts(df9['period_tf4'])

# Now, naming the intervals; must be unique names. 3 intervals
tfs = ["start", "middle", "end"]
df9['period_tf3'] = pd.cut(df9['periodTime'].astype(float), [   0.,  300.,  900., 1200.], labels=tfs)
pd.value_counts(df9['period_tf3'])

# ANGLES -|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|

# 15º INTERVALS FOR ANGLES
ags = ["-90º  -  -75º", "-74º  -  -60º", "-59º  -  45º", "-44º  -  -30º","-29º  -  -15º", "-14º  -  -1º", "0º", "1º  -  15º", "16º  -  30º","31º  -  45º", "46º  -  60º", "61º  -  75º", "76º  -  90º"]
df9['angle_bin15'] = (pd.cut(df9['angle'].astype(float), [ -90., -75., -60., -45., -30., -15.,-1., 1., 15., 30., 45., 60., 75., 90.], labels=ags)).astype(str)
pd.value_counts(df9['angle_bin15']).sort_index()

# 30º INTERVALS FOR ANGLES
ags = ["-90º  -  -60º", "-59º  -  30º", "-29º  -  -1º", "0º", "1º  -  29º", "30º  -  59º", "60º  -  90º"]
df9['angle_bin30'] = (pd.cut(df9['angle'].astype(float), [ -90., -60., -30., -1., 1.,  30., 60., 90.], labels=ags)).astype(str)

# AFOREMENTIONED STUDY INTERVALS FOR ANGLES
ags = ["-90º  -  -46º", "-45º  -  31º", "-30º  -  -16º",  "-15º  -  -1º", "0º", "1º  -  15º", "16º  -  30º", "31º  -  45º", "46º  -  90º"]
df9['angle_bin_STUDY'] = (pd.cut(df9['angle'].astype(float), [ -90., -45., -30.,-15., -1., 1., 15., 30., 45., 90.], labels=ags)).astype(str)



df9.head(5)

# .sort_values(by='angle_bin')
# df9['period_time_bin'].value_counts()
# pd.crosstab(df9.period_tf3, df9.period)
# pd.crosstab(df9.period_tf4, df9.period)
# angle category validation
pd.value_counts(df9['angle_bin15']).sort_index()
pd.value_counts(df9['angle_bin30']).sort_index()
pd.value_counts(df9['angle_bin_STUDY']).sort_index()

df9.groupby(df9['angle_bin15'])['angle'].agg(["max","min"])
df9.groupby(df9['angle_bin30'])['angle'].agg(["max","min"])
df9.groupby(df9['angle_bin_STUDY'])['angle'].agg(["max","min"])

"""## **Validation Prior to Output**"""

# VALIDATION - 1 GAME
events = ['2012020001']
df_test= df9[df9.game_id.isin(events)]
df_test

"""### **Exporting to CSV**"""

df9.to_csv("C:\musical_data\shots.csv" , sep=';' )