"""
Purpose:
Runs semantic analysis on the tweets extracted with 00_*.py, using text_to_x semantic analysis codes
Possibly visualizes?
"""

import text_to_x as ttx
import pandas as pd

df = pd.read_csv("../data/MF_data.csv")
df.columns = df.iloc[0]
df = df.drop([0], axis=0).reset_index(drop=True)

# VADER SENTIMENT
print("Conducting SA with VADER")
tts = ttx.TextToSentiment(lang='da', method="dictionary")
out = tts.texts_to_sentiment(list(df['text'].values))
df = pd.concat([df, out], axis=1)
print("Joining SA results")
#sent_df = sent_df.join(output_long_df)

print(df.head())

filename = "../MF_data_SA.csv"
df.to_csv(filename, index = False)