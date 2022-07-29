import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv, sys, os, json

measurement_data = pd.DataFrame([])
for file in ['ceragon_RxLevel_7d.txt', 'ceragon_RxLevel_7d_2.txt', 'ceragon_RxLevel_7d_3.txt',
        'ceragon_RxLevel_7d_4.txt', 'ceragon_RxLevel_7d_5.txt']:
    data = pd.read_csv('./osnabrueck/' + file, sep=';', header=None)
    data.columns = ['ts', 'rx_power', '']
    measurement_data = pd.concat([measurement_data, data])

measurement_data = measurement_data.sort_values(by = ['ts'])

json_files_archive = os.listdir('./osnabrueck/Westerberg_13_06_to_10_07')
temperature, timestamps, humidity, air_pressure, rain, thunder, wind_speed = [], [], [], [], [], [], []

for json_file in json_files_archive:
    if json_file == "forecast":
        continue
    with open('./osnabrueck/Westerberg_13_06_to_10_07/' + json_file) as f:
        data = json.load(f)
        try:
            temperature.append(data['weather']['WesterbergWetter']['temperature'])
            humidity.append(data['weather']['WesterbergWetter']['humidity'])
            air_pressure.append(data['weather']['WesterbergWetter']['air_pressure'])
            rain.append(data['weather']['WesterbergWetter']['rain'])
            wind_speed.append(data['weather']['WesterbergWetter']['wind_speed'])
            thunder.append(data['weather']['WesterbergWetter']['thunder'])
            timestamps.append(data['time'])
        except:
            pass

measurement_data = measurement_data[measurement_data.ts > timestamps[0]]

for condition in [temperature, humidity, air_pressure, rain, thunder, wind_speed]:
    ax1 = measurement_data.plot(x = 'ts', y = 'rx_power', color = 'g')
    ax1.set_ylim(34, 38)
    ax2 = ax1.twinx()

    ax2.plot(timestamps, condition, color = 'r')

    plt.show()
    plt.close()