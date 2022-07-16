import pandas as pd
import scipy.stats as stats
import os
import abstract_weather_api
import numpy as np
import itertools
weather_kinds = vars(abstract_weather_api.WeatherInformation()).keys()
weather_kinds_ignore = {"time", "last_updated", "location", "sun_rise", "description", "sun_set"}
weather_kinds = [w for w in weather_kinds if w not in weather_kinds_ignore]
weather_api={t.__name__ for  t in abstract_weather_api.apis_dict_reversed}
weather_api=weather_api-{"AccuWeather"}

precision={
    "temperature":5,
    "rain":1,
    "humidity":5,
    "wind_speed":10,
    "air_pressure":1,
    "thunder":1
}
INVALID=-1000
def round_down(m, n):
    if n ==0:
        return m
    return m // n * n
pairs=[a for a in itertools.product(weather_api,weather_api) if a[0]!=a[1]]
OUTLINERS_SIGNIFICANCE=0.05
DIFF_SIGNIFICANCE=0.1
weather_comp_stats=dict()
api_similar=dict()
for w in  os.listdir("time_series"):
    df=pd.read_csv("time_series/"+w,delimiter=";")
   
    for p1,p2 in pairs:
        if p1 not in df or p2 not in df:
            continue
        filtered=[x for x in zip(df[p1],df[p2]) if x[0]!=INVALID and x[1]!=INVALID]
        filtered1=[x[0] for x in filtered]
        filtered2=[x[1] for x in filtered]
        
       # df[p1]=df.apply(lambda row: round_down(row[p1],precision[w]),axis=1)
        #df[p2]=df.apply(lambda row: round_down(row[p2],precision[w]),axis=1)
        #print(np.max(np.abs(df[p1]-df[p2])))
        try:
            #wil=stats.wilcoxon(filtered1,y=filtered2).pvalue
            #kol=stats.ks_2samp(filtered1,filtered2).pvalue
            mx=np.nanmax(filtered)
            mn=np.nanmin(filtered)
            span=mx-mn
            if np.isnan(span):
                continue
            #print("Length",len(filtered))
            #print("span",p1,p2,w,mx,mn,span)
            rel_diff=[abs(x[0]-x[1])/span for x in filtered]
            outliners_share=len([r for r in rel_diff if r >=DIFF_SIGNIFICANCE])/len(rel_diff)
            if w.startswith("humidity"):
                print(p1,p2,mx,mn,span,outliners_share,np.nanmax(rel_diff))
            if outliners_share <OUTLINERS_SIGNIFICANCE and outliners_share>0:
                if w not in weather_comp_stats:
                    weather_comp_stats[w]=[]
                    api_similar[w]=set()
                weather_comp_stats[w]+=[(p1,p2,mx,mn,span,outliners_share)]
                api_similar[w]=api_similar[w] | {p1, p2}
        except Exception as ex:
            raise ex
print("#"*100)
for k in weather_comp_stats:
    print(k)
    for x in weather_comp_stats[k]:
        print(x)
    print(api_similar[k])
    print()

        
