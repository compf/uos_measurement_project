import pandas as pd
import scipy.stats as stats
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
SIGNIFICANCE=0.01
for w in weather_kinds:
    df=pd.read_csv("time_series/"+w+".csv",delimiter=";")
   
    for p1,p2 in pairs:
        filtered=[x for x in zip(df[p1],df[p2]) if x[0]!=INVALID and x[1]!=INVALID]
        filtered1=[round_down(x[0],precision[w]) for x in filtered]
        filtered2=[round_down(x[1],precision[w]) for x in filtered]
        
       # df[p1]=df.apply(lambda row: round_down(row[p1],precision[w]),axis=1)
        #df[p2]=df.apply(lambda row: round_down(row[p2],precision[w]),axis=1)
        #print(np.max(np.abs(df[p1]-df[p2])))
        try:
            wil=stats.wilcoxon(filtered1,y=filtered2).pvalue
            kol=stats.ks_2samp(filtered1,filtered2).pvalue
        
            print("Wilcoxon",w,p1,p2,wil,wil>=SIGNIFICANCE)
            print("Kolmogorov",w,p1,p2,kol,kol>=SIGNIFICANCE)
        except:
            pass
        print()