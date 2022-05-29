import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

apis_names = [
    "BuienRadar",
    "OpenWeatherMap",
    # "AccuWeather",
    "WeatherAPI",
    "WeatherBitIO"]

class WeatherGraphs:
    def __init__(self, apisNames, size):
        self.graphSize = size
        ping_data = []
        apis_data = {}

        for api in apis_names:
            apis_data[api] = []

        for subdir, dirs, files in os.walk('project_archive'):
            for file in files:
                # Opening JSON file
                f = open('project_archive/' + file)

                data = json.load(f)

                ping_data.append(
                    [datetime.fromtimestamp(data['time']), data['ping_result']['avg_rtt'], data['ping_result']['loss'],
                     data['ping_result']['max_rtt'], data['ping_result']['min_rtt']])

                for api in apis_names:
                    if api in data['weather'] and data['weather'][api] is not None:
                        rain = 0
                        if data['weather'][api]['rain'] != 'null' and data['weather'][api]['rain'] != False and \
                                data['weather'][api]['rain'] != None:
                            rain = data['weather'][api]['rain']
                        thunder = 0
                        if data['weather'][api]['thunder'] != 'null' and data['weather'][api]['thunder'] != False and \
                                data['weather'][api]['thunder'] != None:
                            rain = data['weather'][api]['thunder']
                        if api == 'WeatherAPI':
                            data['weather'][api]['wind_speed'] /= 3.6
                        apis_data[api].append(
                            [datetime.fromtimestamp(data['time']), data['weather'][api]['temperature'],
                             data['weather'][api]['humidity'],
                             data['weather'][api]['wind_speed'], data['weather'][api]['air_pressure'],
                             rain, thunder])

        self.ping_df = pd.DataFrame(ping_data,
                               columns=['time', 'avg_rtt', 'loss', 'max_rtt', 'min_rtt'])
        self.ping_df.set_index("time", inplace=True)

        self.apis_df = {}
        self.attibutes = ['Temperature', 'Humidity', 'Wind Speed', 'Air Pressure', 'Rain', 'Thunder']
        for api in apis_names:
            self.apis_df[api] = pd.DataFrame(apis_data[api],
                                        columns=['time'] + self.attibutes)
            self.apis_df[api].set_index("time", inplace=True)

    def compare_apis(self, is_show):
        for att in self.attibutes:
            plt.figure(figsize=self.graphSize)
            ax = plt.gca()
            for api in apis_names:
                self.apis_df[api].plot(kind='line', y=att, label=api, ax=ax)
            # apis_df['WeatherBitIO'].plot(kind='line', y='temperature', ax=ax)
            ax.set_xlabel('Time')
            ax.set_ylabel(att)
            plt.title("APIs Comparison: " + att)

            if is_show:
                plt.show()
            else:
                plt.savefig('graphs/' +"APIs Comparison " + att+'.png')
            #plt.clf()


    def one_api_vs_weather(self, APIName, features, is_show):
        for att in self.attibutes:
            fig, ax1 = plt.subplots()
            fig.set_figheight(self.graphSize[1])
            fig.set_figwidth(self.graphSize[0])
            ax2 = ax1.twinx()
            for feature in features:
                ax1.plot(self.ping_df[feature], label=feature)
            #ax1.plot(self.ping_df['max_rtt'], 'r-', label='max rtt')
            ax2.plot(self.apis_df[APIName][att], 'r-', label=att)

            ax1.set_xlabel('Time')
            #ax1.set_ylabel('RTT', color='g')
            ax2.set_ylabel(APIName +' ' + att, color='b')
            plt.title("["+",".join(features)+ "] vs "+APIName+" " + att)
            ax1.legend(loc=2)
            ax2.legend(loc=1)

            if is_show:
                plt.show()
            else:
                plt.savefig('graphs/' +"["+",".join(features)+ "] vs "+APIName+" " + att + '.png')


def main():
    wg = WeatherGraphs(apis_names, (12, 8))
    wg.compare_apis(True)
    wg.one_api_vs_weather('BuienRadar', ['avg_rtt'],True)


if __name__ == "__main__":
    main()
