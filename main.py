import pandas as pd
import re
from icecream import ic

import seaborn as sns; sns.set()
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pyplot_themes as themes

def remove_mentions(row):
    tweet = row["text"]
    clean_tweet = re.sub(r'@(\S*)\w', '', tweet)
    # Remove URLs
    url_pattern = re.compile(
        r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})')
    clean_tweet = re.sub(url_pattern, '', clean_tweet)
    return clean_tweet

# Aggregate a frequency DF
def get_tweet_frequencies(df):
    # Add freq of hashtags by themselves in the dataset
    tweet_freq = pd.DataFrame({'nr_of_tweets' : df.groupby(['date']).size()}).reset_index()

    # Add the whole_frew to id_hashtag
    freq_hashtags = pd.merge(df, tweet_freq, how='left', on=['date'])#, 'id', 'created_at'])
    
    df0 = freq_hashtags
    return df0

import re

def extract_hashtags(row):
    unique_hashtag_list = list(re.findall(r'#\S*\w', row["text"]))
    return unique_hashtag_list

def hashtag_per_row(data):
    # Create hashtags column with the actual unique hashtags
    data["hashtags"] = data.apply(lambda row: extract_hashtags(row), axis = 1)

    # Let's take a subset of necessary columns, add id
    df = data[["date", "hashtags"]].reset_index().rename(columns={"index": "id"})

    # Select only the ones where we have more than 1 hashtag per tweet
    df = df[df["hashtags"].map(len) > 1].reset_index(drop=True)

    # Hashtag per row
    # convert list of pd.Series then stack it
    df = (df
     .set_index(['date','id'])['hashtags']
     .apply(pd.Series)
     .stack()
     .reset_index()
     .drop('level_2', axis=1)
     .rename(columns={0:'hashtag'}))
    #lowercase!
    df["hashtag"] = df["hashtag"].str.lower()
    df["hashtag"] = df["hashtag"].str.replace("'.", "")
    df["hashtag"] = df["hashtag"].str.replace("’.", "")

    return df

#freq_df["hashtags"] = freq_df.apply(lambda row: extract_b117(row), axis = 1)

# Aggregate a frequency DF
def get_hashtag_frequencies(df):
    # Add freq of hashtags by themselves in the dataset
    tweet_freq = pd.DataFrame({'nr_of_hashtags' : df.groupby(['hashtag']).size()}).reset_index()

    # Add the whole_frew to id_hashtag
    #freq_hashtags = pd.merge(df, tweet_freq, how='left', on=['date'])#, 'id', 'created_at'])
    
    #df0 = freq_hashtags
    return tweet_freq




df = pd.read_csv("data/MF_data.csv")
df.columns = df.iloc[0]
df = df.drop([0], axis=0).reset_index(drop=True)
print(len(df))

rmv_list = []
for i in df.created_at:
    try:
        p = pd.to_datetime(i, utc=True)
    except:
        print("broken_data", i)
        rmv_list.append(i)
        
### REMOVE QUOTE TWEETS ###

#rmv_list = ["created_at", "0"]
df = df[~df["created_at"].isin(rmv_list)]
df = df.reset_index(drop=True)

df["mentioneless_text"] = df.apply(lambda row: remove_mentions(row), axis = 1)
#df["text30"] = df["mentioneless_text"].str[0:30]
#df["text40"] = df["mentioneless_text"].str[0:40]
df["text50"] = df["mentioneless_text"].str[0:50]

#df["dupe30"] = df["text30"].duplicated(keep = "first")
#df["dupe40"] = df["text40"].duplicated(keep = "first")
df["dupe50"] = df["text50"].duplicated(keep = "first")

#ic(len(df[df["dupe30"] == True]))
#ic(len(df[df["dupe40"] == True]))
print("Length of duplicates")
ic(len(df[df["dupe50"] == True]))

df = df[df["dupe50"] == False].reset_index()

### VISUALIZE ###
# Create a column which is just date
df["date"] = pd.to_datetime(df["created_at"], utc=True).dt.strftime('%Y-%m-%d')

freq_df = get_tweet_frequencies(df)

print("Average tweet number per day etc:", freq_df.nr_of_tweets.describe())

freq_df["date"] = pd.to_datetime(freq_df["date"])


###########################################################
matplotlib.rc('ytick', labelsize=20)
matplotlib.rc('xtick', labelsize=20)

nr_colors = len(freq_df["date"].unique())

themes.theme_minimal(grid=False, ticks=False, fontsize=18)
a4_dims = (25,15) #(11.7, 8.27)

palette = sns.color_palette("inferno", nr_colors)

fig, (ax1) = plt.subplots(1,1, figsize=a4_dims)
sns.set(font_scale = 2)
ax1 = sns.lineplot(x="date", y="nr_of_tweets", 
                  palette = palette, 
                     linewidth = 5, data = freq_df)


ax1.set(xlabel="", ylabel = "")
ax1.xaxis.get_label().set_fontsize(40)
ax1.yaxis.get_label().set_fontsize(40)

ax1.grid(color='grey', linestyle='-', linewidth=0.5, which= "both")

# Define the date format
ax1.xaxis_date()
date_form = mdates.DateFormatter("%d-%m")
ax1.xaxis.set_major_formatter(date_form)

    
fig.suptitle("Mentions of MetteF", size = "40")
#ax1.set_title('Level 1', fontsize=30)

#ax1.legend_.remove()

plot_name = "fig/tweet_frequency.png"
fig.savefig(plot_name)

#fig.show()
############################################################


###### HASHTAGS ############################################
hashtags = hashtag_per_row(freq_df)
freq_hashtags = get_hashtag_frequencies(hashtags)
df0 = freq_hashtags.sort_values(by=['nr_of_hashtags'], ascending=False)

import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import pyplot_themes as themes

df0 = df0.nlargest(30, columns=['nr_of_hashtags'])
nr_hash = len(df0["hashtag"].unique())

themes.theme_minimal(grid=False, ticks=False, fontsize=18)
palette = sns.color_palette("inferno", nr_hash)
fig, (ax) = plt.subplots(1,1, figsize=a4_dims)
ax = sns.barplot(y="hashtag", x="nr_of_hashtags", palette = palette, data = df0)

ax.set(xlabel="Count", ylabel = "Hashtag")
ax.xaxis.get_label().set_fontsize(25)
ax.yaxis.get_label().set_fontsize(25)
ax.axes.set_title("Most frequent hashtags",fontsize=30)

#plt.xticks(fontsize=20)
#plt.yticks(fontsize=15)

plot_name = "fig/frequent_hashtags.png"
fig.savefig(plot_name)
###########################################################

######### SENTIMENT #######################################
df = pd.read_csv("MF_data_SA.csv")

##
print(len(df))

rmv_list = []
for i in df.created_at:
    try:
        p = pd.to_datetime(i, utc=True)
    except:
        print("broken_data: ", i)
        rmv_list.append(i)
        
### REMOVE QUOTE TWEETS ###

#rmv_list = ["created_at", "0"]
df = df[~df["created_at"].isin(rmv_list)]
df = df.reset_index(drop=True)
##

df["date"] = pd.to_datetime(df["created_at"], utc=True).dt.strftime('%Y-%m-%d')

df["date"] = pd.to_datetime(df["date"])
# Rolling average
df['compound_7day_ave'] = df.compound.rolling(7).mean().shift(-3)


matplotlib.rc('ytick', labelsize=20)
matplotlib.rc('xtick', labelsize=20)


themes.theme_minimal(grid=False, ticks=False, fontsize=18)
a4_dims = (25,15) #(11.7, 8.27)


fig, (ax1) = plt.subplots(1,1, figsize=a4_dims)
sns.set(font_scale = 2)
ax1 = sns.lineplot(x="date", y="compound", 
                   label="Daily",
                     linewidth = 2, data = df)

ax1 = sns.lineplot(x="date", y="compound_7day_ave", 
                   label="7 Day Average", color = "red",
                     linewidth = 3, data = df)


ax1.set(xlabel="", ylabel = "")
ax1.xaxis.get_label().set_fontsize(40)
ax1.yaxis.get_label().set_fontsize(40)

ax1.grid(color='grey', linestyle='-', linewidth=0.5, which= "both")

# Define the date format
ax1.xaxis_date()
date_form = mdates.DateFormatter("%d-%m")
ax1.xaxis.set_major_formatter(date_form)

    
fig.suptitle("Sentiment analysis of mentions of Mette Frederiksen", size = "40")
#ax1.set_title('Level 1', fontsize=30)

#ax1.legend_.remove()
ax1.set(ylim=(-1, 1))

plot_name = "fig/sentiment_compound.png"
fig.savefig(plot_name)

fig.show()