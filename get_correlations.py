# tool to create correlation diagrams
import os, json, sys, math, time
import matplotlib.pyplot as plt
import abstract_weather_api
import numpy as np
from datetime import datetime
from scipy import stats
SIGNIFICANCE=0.05
apis_names = [
    "BuienRadar",
    "OpenWeatherMap",
    "AccuWeather",
    "WeatherAPI",
    "WeatherBitIO",
    "Meteomatics",
    "Aeris",
    "Foreca"
]

ARCHIVE_PATH = './project_archive'

weather_kinds = vars(abstract_weather_api.WeatherInformation()).keys()
weather_kinds_ignore = {"time", "last_updated", "location", "sun_rise", "description", "sun_set"}
weather_kinds = [w for w in weather_kinds if w not in weather_kinds_ignore]

class APIWeatherInfo:
    def __init__(self, name,time_type):
        self.api_name = name
        self.times = []
        self.time_type=time_type
        self.measurement_results = {
            'avg_rtt': [],
            'max_rtt': [],
            'min_rtt': [],
            "iperf_throughput":[],
            "iperf_retransmission":[]
        }
        self.weather = {}
        for kind in weather_kinds:
            self.weather[kind] = []
        self.correlations = {'avg_rtt': {}, 'max_rtt': {}, 'min_rtt': {},"iperf_throughput":{},
            "iperf_retransmission":{}}
        self.significance = {'avg_rtt': {}, 'max_rtt': {}, 'min_rtt': {},"iperf_throughput":{},
            "iperf_retransmission":{}}
    def is_time_ok(self,t:float,json_obj):
        if "OpenWeatherMap" not in  json_obj["weather"]:
            dt=datetime.fromtimestamp(t)
            
            hour=5
            minute=30
            #hour,minute=json_obj["weather"]["WeatherBitIO"]["sun_set"].split(":")
            dt=datetime(dt.year,dt.month,dt.day,int(hour),int(minute),dt.second)
          
            sun_rise=dt.timestamp()
            # defining sunset only when it is clearly dark because 19:00 it is still too light
            # still need to find better time
            hour=23
            minute=59
            dt=datetime(dt.year,dt.month,dt.day,int(hour),int(minute),dt.second)

            sun_set=dt.timestamp()
        else:
            sun_set=json_obj["weather"]["OpenWeatherMap"]["sun_set"]
            sun_rise=json_obj["weather"]["OpenWeatherMap"]["sun_rise"]
        if self.time_type=="day":
            return t>= sun_rise and t<=sun_set
        elif self.time_type== "night":
            return t<sun_rise or t>sun_set
        else: 
            return True
    def get_correlations(self):
        NO_SIGNIFICANCE=-1000
        HAS_SIGNIFICANCE=0.5
        for kind in self.weather:
            for correlation in self.correlations:
                x = np.array(self.measurement_results[correlation])
                y = np.array(self.weather[kind])
                if len(x)<len(y):
                    #cut off y values that have no associated x values
                    y=y[len(y)-len(x):]
                try:
                    r,p = stats.pearsonr(x,y)
                    # r is the perarson coefficient, p is the significance 
                    print(r,p,correlation,kind,self.api_name,p<SIGNIFICANCE)
                    if math.isnan(r):
                        self.correlations[correlation][kind] = 0
                        self.significance[correlation][kind] =NO_SIGNIFICANCE
                    else:
                        self.correlations[correlation][kind] = r
                        self.significance[correlation][kind] =r+np.sign(r)*HAS_SIGNIFICANCE if  p<SIGNIFICANCE else NO_SIGNIFICANCE
                except Exception as e:
                    self.correlations[correlation][kind] = 0
                    self.significance[correlation][kind] =NO_SIGNIFICANCE


    def plot(self):
        width = 0.2
        width_significance=0.02
        x = np.arange(6)
        plt.bar(x-0.3, list(self.correlations['avg_rtt'].values()), width, color='r', edgecolor='r', label='Avg. RTT')
        plt.bar(x-0.1, list(self.correlations['max_rtt'].values()), width, color='g', edgecolor='g', label='Max. RTT')
        plt.bar(x+0.1, list(self.correlations['min_rtt'].values()), width, color='b', edgecolor='b', label='Min. RTT')
        
        plt.scatter(x-0.3, list(self.significance['avg_rtt'].values()),  c="black", marker="x",  label='_nolegend_')
        plt.scatter(x-0.1, list(self.significance['max_rtt'].values()),   c="black",marker="x" , label='_nolegend_')
        plt.scatter(x+0.1, list(self.significance['min_rtt'].values()),   c="black",marker="x"  ,label='_nolegend_')
        #plt.bar(x+0.3, list(self.correlations['loss'].values()),    width, color='y', edgecolor='black', label='Loss')

        plt.xticks(x, [kind for kind in self.weather])
        plt.ylabel('Correlation')
        plt.title(f'Correlation of API \'{self.api_name}\' with weather in Laar', fontsize=14)
        plt.legend(loc='upper right')
        plt.grid()
        plt.ylim(-1, 1)
        plt.tight_layout()
        plt.savefig(f'./correlationgraphs/correlations_rtt_{self.api_name}_{self.time_type}.pdf')
        plt.clf()

        plt.bar(x-0.2, list(self.correlations['iperf_throughput'].values()), width, color='r', edgecolor='black', label='Iperf throughput')
        plt.bar(x,     list(self.correlations['iperf_retransmission'].values()), width, color='g', edgecolor='black', label='Iperf retransmission')
        plt.scatter(x-0.2, list(self.significance['iperf_throughput'].values()),  c="black",marker="x",  label='_nolegend_')
        plt.scatter(x, list(self.significance['iperf_retransmission'].values()),   c="black", marker="x", label='_nolegend_')
        plt.xticks(x, [kind for kind in self.weather])
        plt.ylabel('Correlation')
        plt.title(f'Correlation of API \'{self.api_name}\' with weather in Laar', fontsize=14)
        plt.legend(loc='upper right')
        plt.grid()
        plt.ylim(-1, 1)
        plt.tight_layout()
        plt.savefig(f'./correlationgraphs/correlations_iperf_{self.api_name}_{self.time_type}.pdf')
        plt.clf()


def main():
    json_files = os.listdir(ARCHIVE_PATH)
    data = []
    print("load")
    for json_file in json_files:
        if json_file=="forecast":
            continue

        with open(ARCHIVE_PATH + '/' + json_file) as f:
            data.append(json.load(f))

    data = sorted(data, key = lambda x : x["time"])
    
    apiWeatherInformations = []
    for api in apis_names:
        apiWeatherInformations.append(APIWeatherInfo(api,"all"))
        apiWeatherInformations.append(APIWeatherInfo(api,"day"))
        apiWeatherInformations.append(APIWeatherInfo(api,"night"))
    # load the data
    for d in data:
        for api in apis_names:
            if not api in d['weather'] or d['weather'][api] == None:
                continue
            for apiWeatherInfo in apiWeatherInformations:
                if apiWeatherInfo.api_name == api:
                    if  not apiWeatherInfo.is_time_ok(d["time"],d):
                        continue
                    apiWeatherInfo.times.append(d['time'])
                    apiWeatherInfo.measurement_results['avg_rtt'].append(d['ping_result']['avg_rtt'])
                    apiWeatherInfo.measurement_results['max_rtt'].append(d['ping_result']['max_rtt'])
                    apiWeatherInfo.measurement_results['min_rtt'].append(d['ping_result']['min_rtt'])
                    if "iperf_result" in d:
                        apiWeatherInfo.measurement_results['iperf_throughput'].append(d['iperf_result']['bits_per_sec'])
                        apiWeatherInfo.measurement_results['iperf_retransmission'].append(d['iperf_result']['retransmissions'])
                    for kind in weather_kinds:
                        apiWeatherInfo.weather[kind].append(d['weather'][api][kind])
            
    for apiWeatherInfo in apiWeatherInformations:
        apiWeatherInfo.get_correlations()
        apiWeatherInfo.plot()


if __name__ == "__main__":
    main()
