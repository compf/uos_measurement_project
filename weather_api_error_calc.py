import abstract_weather_api
import numpy as np
import json
import os
import math
import itertools
from scipy import stats
weather_kinds_ignore={"time","last_updated","location","sun_rise","description","sun_set"}

weather_information=[w for w in abstract_weather_api.WeatherInformation().__dict__ if w not in weather_kinds_ignore]
def get_weather_stats(pair):
    p1,p2=pair
    times=dict()
    
    result=dict()
    for p in os.listdir("project_archive"):
        if p=="forecast":
            continue
        with open("project_archive/"+p) as f:
            json_obj=json.load(f)
            if p1 in json_obj["weather"] and p2 in json_obj["weather"] and  json_obj["weather"][p1]!=None and  json_obj["weather"][p2]!=None:
                weather_data=dict()
                for w in weather_information:
                    weather_data[w]=(json_obj["weather"][p1][w],json_obj["weather"][p2][w])

                    result[json_obj["time"]]=weather_data
    return result
def kolgomorov_smirov(pair_result):
    result=dict()
    for w in weather_information:
        if w=="thunder":
            continue
        com1=[pair_result[t][w][0] if pair_result[t][w][0]!=None else 0 for t in pair_result]
        com2=[pair_result[t][w][1] if pair_result[t][w][1]!=None else 0 for t in pair_result]
        
        if len(com1)==0 or len(com2)==0:
            continue
        print("Weather",w)
        cumA,cumB=0,0
        for p in zip(com1,com2):
            print(p[0],p[1],abs(p[0]-p[1]),abs(cumA-cumB))
            cumA+=p[0]
            cumB+=p[1]
        res=stats.ks_2samp(com1,com2)
        result[w]=res.pvalue
    return result
def avg_abs_diff(pair_result):
    averages=dict([(w,[]) for w in weather_information])
    for t in pair_result:
        for w in pair_result[t]:
            w1,w2=pair_result[t][w]
            if (isinstance(w1,float) or isinstance(w1,int)) and ( isinstance(w2,int) or isinstance(w2,float)):
                averages[w].append(abs(w1-w2))
    for w in averages:
        mean=np.mean(averages[w])
        if math.isnan(mean):
            averages[w]=10e10
        else:
            averages[w]=mean
    return averages
def pearson(pair_result,p):
    averages=dict([(w,[]) for w in weather_information])
    for t in pair_result:
        for w in pair_result[t]:
            w1,w2=pair_result[t][w]
            
            if (isinstance(w1,float) or isinstance(w1,int)) and ( isinstance(w2,int) or isinstance(w2,float)) and not isinstance(w1,bool) and not isinstance(w2,bool):
                averages[w].append([w1,w2])
    for w in averages:
        print("Weather" ,w,p)
        print(averages[w])
        if len(averages[w])==0:
            averages[w]=10e10
        else:
          
            averages[w]=np.corrcoef(averages[w],rowvar=False)[0][1]
            print("test",averages[w])
    return averages
api_names=[a.__name__ for a in abstract_weather_api.apis_dict.values()]
api_pairs=[ frozenset(p) for p  in itertools.product(api_names,repeat=2) if len(set(p))>1]
print(api_pairs)
avg_result=dict()
corr_result=dict()
SIGNIFICANCE=0.5
for p in api_pairs:
    pair_result=get_weather_stats(p)
        #abs_avg=avg_abs_diff(pair_result)

        #corr=pearson(pair_result,p)
        #avg_result[p]=abs_avg
       # corr_result[p]=corr
    print("#"*100)
    print(p)
    pVals=kolgomorov_smirov(pair_result)
    for w in pVals:
        print(w,pVals[w],pVals[w]>=SIGNIFICANCE)


