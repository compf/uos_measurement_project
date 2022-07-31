# get thunder information from descriptions
import os
import json
import pandas as pd


thunder_description={"Isolated Thunderstorms",'Thunderstorm with heavy rain','Patchy light rain with thunder',
'Thundery outbreaks possible','Chance of Strong Thunderstorms'}
def is_thunder(descr,time,api)->bool:
    if descr==None:
        return False
    if descr in thunder_description:
        return True
    elif api=="Foreca" and (description.startswith("d4") or description.startswith("n4")):
        return True
    else:
        return False
api_times=set()

for p in os.listdir("project_archive/"):
   
    with open("project_archive/"+p) as f:
        json_obj=json.load(f)
        time=json_obj["time"]
        for a in json_obj["weather"]:
            if json_obj["weather"][a]==None:
                continue
            description=json_obj["weather"][a]["description"]
            thunder=is_thunder(description,time,a)
            if thunder:
                json_obj["weather"][a]["thunder"]=1
                api_times.add((a,time))
            else:
                json_obj["weather"][a]["thunder"]=0
    with open("../project_archive/"+p,"w") as f:
        json.dump(json_obj,f)

df=pd.read_csv("../time_series/thunder.csv",delimiter=";")
df=df.set_index("Time")

for a,t in api_times:
    df.loc[t,a]=1
df.to_csv("../time_series/thunder.csv",sep=";")
