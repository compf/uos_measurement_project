import os, json, sys, math, time,csv
import matplotlib.pyplot as plt
import abstract_weather_api
import numpy as np
def transform(value,a,w):
    if (a=="WeatherAPI" or a=="Aeris") and w=="wind_speed":
        return value/3.6
    elif value==False:
        return 0
    elif value==True:
        return 1
    else:
        return value
weather_kinds = vars(abstract_weather_api.WeatherInformation()).keys()
weather_kinds_ignore = {"time", "last_updated", "location", "sun_rise", "description", "sun_set"}
weather_kinds = [w for w in weather_kinds if w not in weather_kinds_ignore]
weather_api=[t.__name__ for  t in abstract_weather_api.apis_dict_reversed]
INVALID=-1000
series=dict()
for fname in os.listdir("project_archive"):
    if fname=="forecast":
        continue
    with open("project_archive/"+fname) as f:
        json_obj=json.load(f)
        for w in weather_kinds:
            if w not in series:
                series[w]=[]
           # print(json_obj)
            line=[json_obj["time"]]+[transform(json_obj["weather"][a][w],a,w) if a in json_obj["weather"] and  json_obj["weather"][a]!=None else INVALID for a in weather_api]
            series[w].append(line)
for w in weather_kinds:
    series[w]=sorted(series[w])
    with open("time_series/"+w+".csv","w+",newline='') as f:
        writer=csv.writer(f,delimiter=";")
       #print(series[w])
        writer.writerow(["Time"]+weather_api)
        for s in series[w]:
            writer.writerow (s)
