import os, json, sys, math, pickle
from datetime import datetime
import matplotlib.pyplot as plt
import abstract_weather_api
import numpy as np
import pandas as pd

apis_names = [
    'WesterbergWetter', 
    'Weatherbit'
]

ARCHIVE_PATH    = './osnabrueck/Westerberg_13_06_to_10_07'
HISTORIC_PATH   = './osnabrueck/historic_data_osna'
DATA_PATH       = './osnabrueck/'

weather_kinds = vars(abstract_weather_api.WeatherInformation()).keys()
weather_kinds_ignore = {"time", "last_updated", "location", "sun_rise", "description", "sun_set", 'thunder'}
weather_kinds = [w for w in weather_kinds if w not in weather_kinds_ignore]
print(weather_kinds)

class APIWeatherInfo:
    def __init__(self, name):
        self.api_name = name
        self.times = []
        self.measurement_results = {
            'rx_power': []
        }
        self.weather = {}
        for kind in weather_kinds:
            self.weather[kind] = []
        self.correlations = {'rx_power': {}}

    def get_correlations(self):
        for kind in self.weather:
            for correlation in self.correlations:
                try:
                    x = np.array(self.measurement_results[correlation])
                    y = [int(float(i)) for i in self.weather[kind]]
                    y = np.array(y)
                    r = np.corrcoef(x, y)[0, 1]
                    if math.isnan(r):
                        self.correlations[correlation][kind] = 0
                    else:
                        self.correlations[correlation][kind] = r
                except Exception as e:
                    self.correlations[correlation][kind] = 0

    def plot(self, night=False):
        width = 0.2
        x = np.arange(len(weather_kinds))
        plt.bar(x, list(self.correlations['rx_power'].values()), width=width, edgecolor='black', label='Rx Power')

        plt.xticks(x, [kind for kind in self.weather])
        plt.ylabel('Correlation')
        plt.title(f'Correlation of API \'{self.api_name}\' with signal strength', fontsize=14)
        plt.legend(loc='upper right')
        plt.grid()
        plt.ylim(-1, 1)
        plt.tight_layout()
        if night:
            plt.savefig(f'./osnabrueck/correlations_rxpower_night_{self.api_name}.pdf')
        else:
            plt.savefig(f'./osnabrueck/correlations_rxpower_{self.api_name}.pdf')
        plt.close()

    def plot_single_condition(self, night=False):
        for kind in self.weather:
            # zu jedem Datenpunkt in 'kind' Durchschnitt aller Signalstärken bilden 
            plot_data = {}
            for i in range(len(self.weather[kind])):
                if self.weather[kind][i] in plot_data:
                    plot_data[self.weather[kind][i]].append(self.measurement_results['rx_power'][i])
                else:
                    plot_data[self.weather[kind][i]] = [self.measurement_results['rx_power'][i]]

            for item in plot_data:
                plot_data[item] = np.mean(plot_data[item])

            plot_df = pd.DataFrame(list(zip(plot_data.keys(), plot_data.values())), columns = [kind, 'rx_power'])

            if plot_df.empty:
                continue
            
            plot_df[kind] = pd.to_numeric(plot_df[kind])
            plot_df = plot_df.sort_values(by = [kind])
            
            ax1 = plot_df.plot(x = str(kind), y = 'rx_power')
            ax1.set_ylabel('RX Power (dBm)')
            ax1.legend(['RX power'])
            if kind == 'temperature':
                ax1.set_xlabel('Temperature (°C)')
            elif kind == 'humidity':
                ax1.set_xlabel('Humidity (%)')
            
            if night:
                plt.savefig(f'./osnabrueck/plot_{str(kind)}_rxpower_{self.api_name}_night.pdf')
            else:
                plt.savefig(f'./osnabrueck/plot_{str(kind)}_rxpower_{self.api_name}.pdf')
            plt.close()


def is_night(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    hour_sun_rise = 5
    minute_sun_rise = 30
    hour_sun_set = 23
    minute_sun_set = 0

    sun_rise = datetime(dt.year, dt.month, dt.day, int(hour_sun_rise), int(minute_sun_rise), dt.second).timestamp()
    sun_set = datetime(dt.year, dt.month, dt.day, int(hour_sun_set), int(minute_sun_set), dt.second).timestamp()

    return (timestamp < sun_rise or timestamp > sun_set)

def main():
    try:
        with open('apiWeatherInformations.pickle', 'rb') as handle:
            apiWeatherInformations = pickle.load(handle)
        with open('apiWeatherInformations_night.pickle', 'rb') as handle:
            apiWeatherInformations_night = pickle.load(handle)
        print('pickle files found')
    except:
        print('new run, pickle files not found')
        json_files_archive = os.listdir(ARCHIVE_PATH)
        json_files_historic = os.listdir(HISTORIC_PATH)
        data_archive, data_historic = [], []

        for json_file in json_files_archive:
            if json_file == "forecast":
                continue
            with open(ARCHIVE_PATH + '/' + json_file) as f:
                data_archive.append(json.load(f))

        for json_file in json_files_historic:
            if json_file == "forecast":
                continue
            with open(HISTORIC_PATH + '/' + json_file) as f:
                data = json.load(f)
                for d in data['data']:
                    data_historic.append(d)

        data_archive = sorted(data_archive, key = lambda x : x['time'])
        data_historic = sorted(data_historic, key = lambda x : x['ts'])

        measurement_data = pd.DataFrame([])
        for file in ['ceragon_RxLevel_7d.txt', 'ceragon_RxLevel_7d_2.txt', 'ceragon_RxLevel_7d_3.txt',
                'ceragon_RxLevel_7d_4.txt', 'ceragon_RxLevel_7d_5.txt']:
            data = pd.read_csv(DATA_PATH + file, sep=';', header=None)
            data.columns = ['ts', 'rx_power', '']
            measurement_data = pd.concat([measurement_data, data])

        measurement_data = measurement_data.sort_values(by = ['ts'])
        
        apiWeatherInformations = [APIWeatherInfo('WesterbergWetter'), APIWeatherInfo('Weatherbit')]
        apiWeatherInformations_night = [APIWeatherInfo('WesterbergWetter'), APIWeatherInfo('Weatherbit')]

        for d in data_archive:
            try:
                d['weather']['WesterbergWetter']['temperature']
            except Exception as e:
                continue
            for index, row in measurement_data.iterrows():
                if abs(d['time'] - int(row['ts'])) < 600:
                    if is_night(d['time']):
                        apiWeatherInformations_night[0].times.append(d['time'])
                        for kind in weather_kinds:
                            apiWeatherInformations_night[0].weather[kind].append(d['weather']['WesterbergWetter'][kind])
                        apiWeatherInformations_night[0].measurement_results['rx_power'].append(- row['rx_power'])
                    apiWeatherInformations[0].times.append(d['time'])
                    for kind in weather_kinds:
                        apiWeatherInformations[0].weather[kind].append(d['weather']['WesterbergWetter'][kind])
                    apiWeatherInformations[0].measurement_results['rx_power'].append(- row['rx_power'])
                    break

        for d in data_historic:
            for index, row in measurement_data.iterrows():
                if abs(d['ts'] - int(row['ts'])) < 600:
                    if is_night(d['ts']):
                        apiWeatherInformations_night[1].times.append(d['ts'])
                        for kind in weather_kinds:
                            if kind == 'temperature':
                                apiWeatherInformations_night[1].weather[kind].append(d['temp'])
                            elif kind == 'humidity':
                                apiWeatherInformations_night[1].weather[kind].append(d['rh'])
                            elif kind == 'wind_speed':
                                apiWeatherInformations_night[1].weather[kind].append(d['wind_spd'])
                            elif kind == 'air_pressure':
                                apiWeatherInformations_night[1].weather[kind].append(d['pres'])
                        apiWeatherInformations_night[1].measurement_results['rx_power'].append(- row['rx_power'])
                    apiWeatherInformations[1].times.append(d['ts'])
                    for kind in weather_kinds:
                        if kind == 'temperature':
                            apiWeatherInformations[1].weather[kind].append(d['temp'])
                        elif kind == 'humidity':
                            apiWeatherInformations[1].weather[kind].append(d['rh'])
                        elif kind == 'wind_speed':
                            apiWeatherInformations[1].weather[kind].append(d['wind_spd'])
                        elif kind == 'air_pressure':
                            apiWeatherInformations[1].weather[kind].append(d['pres'])
                    apiWeatherInformations[1].measurement_results['rx_power'].append(- row['rx_power'])
                    break
        
        with open('apiWeatherInformations.pickle', 'wb') as handle:
            pickle.dump(apiWeatherInformations, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('apiWeatherInformations_night.pickle', 'wb') as handle:
            pickle.dump(apiWeatherInformations_night, handle, protocol=pickle.HIGHEST_PROTOCOL)

    for apiWeatherInfo in apiWeatherInformations:
        apiWeatherInfo.get_correlations()
        apiWeatherInfo.plot()
        apiWeatherInfo.plot_single_condition()

    for apiWeatherInfo in apiWeatherInformations_night:
        apiWeatherInfo.get_correlations()
        apiWeatherInfo.plot(night=True)
        apiWeatherInfo.plot_single_condition(night=True)


if __name__ == "__main__":
    main()
