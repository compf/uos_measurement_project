import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import json
weather_kinds_ignore = {"time", "last_updated", "location", "sun_rise", "description", "sun_set"}

filenames=["ceragon_RxLevel_7d.txt","ceragon_RxLevel_7d_2.txt"]
filenames=filenames[1:]
weather_data=dict()
for p in os.listdir("project_archive_osna"):

    with open("project_archive_osna/"+p) as f:
        json_obj=json.load(f)
        if json_obj["weather"]!={}:
            weather_data[json_obj["time"]]=json_obj["weather"]["WesterbergWetter"]

for p in filenames:
    with open(p) as f:
        x=[]
        y=[]
        for line in csv.reader(f,delimiter=";"):

            time,db=line[:-1]
            time=int(time)
            db=float(db)
            if time in weather_data:
                x.append(time)
                y.append(-db)
        for  kind in weather_data[time]:
            if kind in  weather_kinds_ignore:
                continue
            fig,ax=plt.subplots()
            ax.set_ylabel("Rx power")
            print(y)
            ax.plot(x,y)
            ax=ax.twinx()
            #ax.set_ylabel(kind)
            y2=[float(weather_data[t][kind]) if weather_data[t][kind]!=None else -1 for t in x ]
            ax.plot(x,y2,color="red")
            fig.suptitle("RX power")
            ax.set_xlabel("Time")
            fig.savefig(p+"_"+kind+".pdf")
            plt.close()

