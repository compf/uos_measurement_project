import os
import json
from typing import Tuple, List
import itertools
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import abstract_weather_api
import numpy as np
import pickle5 as pickle
EXTENSION=".svg"
apis_names =[
    "BuienRadar",
  "OpenWeatherMap",
    "AccuWeather",
   "WeatherAPI",
    "WeatherBitIO",
   "Meteomatics",
    "Aeris",
   "Foreca"
]
weather_kinds=vars(abstract_weather_api.WeatherInformation()).keys()
weather_kinds_ignore={"time","last_updated","location","sun_rise","description","sun_set"}
weather_kinds=[w for w in weather_kinds if w not in weather_kinds_ignore]+["rain_binary"]


raw_json_data = None
time_jsonObj=dict()



def load_all_data():
    global raw_json_data,time_jsonObj
    if raw_json_data == None:
        raw_json_data = []
        for fname in os.listdir("project_archive"):
            if fname=="forecast":
                continue
            with open("project_archive/"+fname) as f:
                json_obj=json.load(f)
                raw_json_data.append(json_obj)
                time_jsonObj[json_obj["time"]]=json_obj
        #raw_json_data=sorted(raw_json_data,lambda x:x["time"])
            

    else:
        s=None
def get_weather_data(json_obj,api_name,weather_kind)->any:
    b= api_name in json_obj["weather"] and   json_obj["weather"][api_name]!=None  and weather_kind in json_obj["weather"][api_name]
    if b:
        return json_obj["weather"][api_name][weather_kind]
    elif weather_kind=="rain_binary" and  api_name in json_obj["weather"] and   json_obj["weather"][api_name]!=None  and "rain" in json_obj["weather"][api_name] and json_obj["weather"][api_name]["rain"]!=None:
          return 1 if  json_obj["weather"][api_name]["rain"]>0 else 0
    else:
        return None
load_all_data()

for a in apis_names:
    for w in weather_kinds:
        count_dict=dict()
        for t in time_jsonObj:
            data=get_weather_data(time_jsonObj[t],a,w)
            if data==None:
                continue
            if data not in count_dict:
                count_dict[data]=0
            count_dict[data]+=1
        plt.figure()
        if len(count_dict)==0:
            continue
        mx,mn=max([k for k in count_dict]),min([k for k in count_dict])
        if mx==mn:
            factor=1
        else:
            factor=100/(mx-mn)
        print(factor)
        plt.bar([1*k for k in count_dict.keys()],count_dict.values())
        plt.savefig(f"frequency_weather/{a}_{w}.svg")
        plt.close()
