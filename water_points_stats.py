import argparse
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import json

def get_water_points_stats(url):
    import json
    from urllib import request
    import pandas as pd
    
    if not url.split('/')[-1].endswith('json'):
        print("Url is not pointing to a json file. Aborting!!!")
        return
    
    with request.urlopen(url) as f:
        content = f.read().decode('utf-8')
        
    df = pd.DataFrame(json.loads(content))
    
    if not "water_functioning" in df or not "communities_villages" in df:
        print("No details found about water points in communities (communities_villages, water_functioning). Aborting!!!")
        return
    
    df['water_functioning'] = df.water_functioning.apply(str.lower)
    
    temp = df.groupby(['communities_villages', 'water_functioning'])['_id'].count().reset_index()
    temp = temp.pivot(index="communities_villages", columns="water_functioning", values="_id").fillna(0)
    temp["perc"] = temp.apply(lambda row: 0 if not row['no'] else int(100*(row['no']/(row['yes'] + row['no']))),axis=1).values
    temp["rank"] = temp.perc.rank(method='first', ascending=False)
    
    #communities = []
    #for row in temp.iterrows():
    #    communities.append({
    #        "communities_villages": row[0],
    #        "total_water_points": int(row[1]["yes"] + row[1]["no"]),
    #        "non_functional": int(row[1]["no"]),
    #        "percentage": int(row[1]["perc"]),
    #        "rank_by_perc": int(row[1]["rank"])
    #    })
    #    
    #output = {
    #    "number_functional" : int(df.groupby('water_functioning')['_id'].count().loc["yes"]),
    #    "communities": communities
    #}
    
    output = {
        "number_functional" : int(df.groupby('water_functioning')['_id'].count().loc["yes"]),
    }
    output["number_water_points"] = {}
    for row in temp.iterrows():
        output["number_water_points"].update({
            row[0]: {
                "total_water_points": int(row[1]["yes"] + row[1]["no"]),
                "non_functional": int(row[1]["no"]),
                "broken_percentage": int(row[1]["perc"]),
            }
        })
    output["community_ranking"] = temp['rank'].astype(int).to_dict()
    
    return output


def parse_args():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--url", type=str, default=None, required=True)
    
    return parser.parse_args()

if __name__ == "__main__":
    output = get_water_points_stats(parse_args().url)
    print("Output saved in current directory: output.json")
    with open("output.json", "w", encoding="utf-8") as jsonfile:
        json.dump(output, jsonfile, ensure_ascii=False)