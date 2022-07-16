import os, json, sys, math, time
import matplotlib.pyplot as plt
import abstract_weather_api
import numpy as np

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
    def __init__(self, name):
        self.api_name = name
        self.times = []
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

    def get_correlations(self):
        for kind in self.weather:
            for correlation in self.correlations:
                x = np.array(self.measurement_results[correlation])
                y = np.array(self.weather[kind])
                if len(x)<len(y):
                    y=y[len(y)-len(x):]
                try:
                    r = np.corrcoef(x, y)[0, 1]
                    print(r,correlation)
                    if math.isnan(r):
                        self.correlations[correlation][kind] = 0
                    else:
                        self.correlations[correlation][kind] = r
                except Exception as e:
                    self.correlations[correlation][kind] = 0

    def plot(self):
        width = 0.2
        x = np.arange(6)
        plt.bar(x-0.3, list(self.correlations['avg_rtt'].values()), width, color='r', edgecolor='black', label='Avg. RTT')
        plt.bar(x-0.1, list(self.correlations['max_rtt'].values()), width, color='g', edgecolor='black', label='Max. RTT')
        plt.bar(x+0.1, list(self.correlations['min_rtt'].values()), width, color='b', edgecolor='black', label='Min. RTT')
        #plt.bar(x+0.3, list(self.correlations['loss'].values()),    width, color='y', edgecolor='black', label='Loss')

        plt.xticks(x, [kind for kind in self.weather])
        plt.ylabel('Correlation')
        plt.title(f'Correlation of API \'{self.api_name}\' with weather in Laar', fontsize=14)
        plt.legend(loc='upper right')
        plt.grid()
        plt.ylim(-0.5, 0.5)
        plt.tight_layout()
        plt.savefig(f'./correlationgraphs/correlations_rtt_{self.api_name}.pdf')
        plt.clf()

        plt.bar(x-0.2, list(self.correlations['iperf_throughput'].values()), width, color='r', edgecolor='black', label='Iperf throughput')
        plt.bar(x,     list(self.correlations['iperf_retransmission'].values()), width, color='g', edgecolor='black', label='Iperf retransmission')

        plt.xticks(x, [kind for kind in self.weather])
        plt.ylabel('Correlation')
        plt.title(f'Correlation of API \'{self.api_name}\' with weather in Laar', fontsize=14)
        plt.legend(loc='upper right')
        plt.grid()
        plt.ylim(-1, 1)
        plt.tight_layout()
        plt.savefig(f'./correlationgraphs/correlations_iperf_{self.api_name}.pdf')
        plt.clf()


def main():
    json_files = os.listdir(ARCHIVE_PATH)
    data = []

    for json_file in json_files:
        if json_file=="forecast":
            continue

        with open(ARCHIVE_PATH + '/' + json_file) as f:
            data.append(json.load(f))

    data = sorted(data, key = lambda x : x["time"])
    
    apiWeatherInformations = []
    for api in apis_names:
        apiWeatherInformations.append(APIWeatherInfo(api))

    for d in data:
        for api in apis_names:
            if not api in d['weather'] or d['weather'][api] == None:
                continue
            for apiWeatherInfo in apiWeatherInformations:
                if apiWeatherInfo.api_name == api:
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