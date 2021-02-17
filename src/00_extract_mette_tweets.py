"""
Purpose: goes through Twitter corpus data and extracts tweets that include mentions of MF, saves them as a separate dataframe

"""

import pandas as pd
import glob
import ndjson
import re
import string

mega_path = mega_path = glob.glob('/data/001_twitter_hope/preprocessed/da/*.ndjson')

i = 0

remove = string.punctuation
remove = remove.replace("#", "") # don't remove hashtags
pattern = r"[{}]".format(remove) # create the pattern

def retrieve_retweets(row):
    if re.match("^RT", row):
        RT = True
    else:
        RT = False
    return RT

def remove_retweets(ori_data):
    patternDel = "^RT"
    data["text"] = data["text"].astype(str)
    filtering = data['text'].str.contains(patternDel)
    removed_RT = ori_data[~filtering].reset_index(drop=True)
    
    return removed_RT

def extract_usernames(row):
    username_list = list(re.findall(r'@(\S*)\w', row["text"]))
    return username_list

def extract_Mette_F(row):
    tweet = row["text"].lower()
    #tweet = tweet.translate(str.maketrans('', '', string.punctuation))
    test_list = ['mettef', 'mettefrederiksen', 'mettefredriksen', 
                 '#mettef', '#mettefrederiksen', '#mettefredriksen',
                 'mette frederiksen', 'mette fredriksen',
                '@statsmin'] 
    res = [ele for ele in test_list if(ele in tweet)] 

    return res
    
for file in mega_path:
    testset = []
    
    file_name = re.findall(r'(td.*)\.ndjson', file)[0]
    
    print("Opening " +  file_name)
          
    with open(file, 'r') as myfile:
        head=myfile.readlines()

    for i in range(len(head)):
        try:
            testset.extend(ndjson.loads(head[i]))
        except:
            print("err in ", file)
            pass
    
    data = pd.DataFrame(testset)
    del testset
    print("Begin processing " +  file_name)

    df = remove_retweets(data)
    
    #df = data
    df["MF"] = df.apply(lambda row: extract_Mette_F(row), axis = 1)

    df = df[["created_at", "id", "text", "MF"]]
    
    df["MF"] = df["MF"].astype(str)
    df2 = df[df["MF"] != "[]"].drop_duplicates().reset_index(drop=True)
        
    filename = "../data/MF_" + file_name + ".csv"
    df2.to_csv(filename, index = False)
    print(df2.head())

    print("Save of " + file_name + " done")
    print("-------------------------------------------\n")
        
    i = i+1