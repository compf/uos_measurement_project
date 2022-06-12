import os
import json
from typing import Tuple, List
import itertools
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import abstract_weather_api
import numpy as np
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
weather_kinds=[w for w in weather_kinds if w not in weather_kinds_ignore]


raw_json_data = None
time_jsonObj=dict()

class WeatherGraphInformation:
    def __init__(self, title: str, x_label: str, y_labels: List[str], path: str,kind:str) -> None:
        self.title = title
        self.x_label = x_label
        self.y_labels = y_labels
        self.path = path
        self.kind=kind # TODO find better solution




class WeatherGraph:

    def __init__(self, x_values, y_values, information: WeatherGraphInformation):
        self.x_values = x_values
        self.y_values = y_values
        self.information = information
    def draw(self):
        colors=["blue","red","green"]
        fig=plt.figure()
        ax = fig.add_subplot(111)
        plt.title(self.information.title)
        plt.xlabel(self.information.x_label)
        first_iteration=None
        counter=0
        lns=[]
        lbls=[]
        for pair in zip(self.y_values,self.information.y_labels):
            if first_iteration:
                ax=ax.twinx()
                first_iteration=False
            ax.plot(self.x_values,pair[0],label=pair[1],color=colors[counter])
    
            counter+=1
            if first_iteration==None:
                first_iteration=True
        base_path=os.path.dirname(self.information.path)
        os.makedirs(base_path,exist_ok=True)
        fig.legend()
        plt.savefig(self.information.path)
        plt.close()

class AbstractDataLoader:
    def load_all_data(self):
        global raw_json_data,time_jsonObj
        if raw_json_data == None:
            self.raw_data = []
            for fname in os.listdir("project_archive"):
                if fname=="forecast":
                    continue
                with open("project_archive/"+fname) as f:
                    json_obj=json.load(f)
                    self.raw_data.append(json_obj)
                    time_jsonObj[json_obj["time"]]=json_obj
            self.raw_data=sorted(self.raw_data,key=lambda x:x["time"])
            
            raw_json_data = self.raw_data

        else:
            s=None
            self.raw_data = raw_json_data

    def load(self) -> List[WeatherGraph]:
        pass


class TimePingDataLoader(AbstractDataLoader):
    def load(self) -> List[WeatherGraph]:
        result=[]
        ping_result_kinds = ["min_rtt", "avg_rtt", "max_rtt"]
        for kind in ping_result_kinds:
            x_data=[]
            y_data=[[]]
            path=f"graphs/time_ping/{kind}"+EXTENSION
            inf=WeatherGraphInformation(f"Time -> Ping ({kind})","Time [s]",[f"Ping ({kind})"],path,kind)
            for json_obj in self.raw_data:
                x_data.append(json_obj["time"])
                y_data[0].append(json_obj["ping_result"][kind])
            result.append(WeatherGraph(x_data,y_data,inf))
        return result
                
def get_weather_data(json_obj,api_name,weather_kind)->any:
    b= api_name in json_obj["weather"] and   json_obj["weather"][api_name]!=None  and weather_kind in json_obj["weather"][api_name]
    if b:
        return json_obj["weather"][api_name][weather_kind]
    else:
        return None

INVALID=-1
class TimePingWeatherLoader(TimePingDataLoader):
    def __init__(self,api_name,weather_kind) -> None:
        super().__init__()
        self.api_name=api_name
        self.weather_kind=weather_kind
    def load(self) -> List[WeatherGraph]:
        base_result= super().load()
        for res in base_result:
            res.information.y_labels.append(self.weather_kind +" from "+self.api_name)
            res.y_values.append([])
            res.information.path=f"graphs/time_ping/weather/{res.information.kind}/{self.api_name}_{self.weather_kind}"+EXTENSION
            y_values=res.y_values[1]
            res.information.kind+=f"_{self.api_name}_{self.weather_kind}"
            for json_obj in self.raw_data:
                weather=get_weather_data(json_obj,self.api_name,self.weather_kind)
                if weather!=None:
                    y_values.append(weather)
                else:
                   
                    y_values.append(INVALID)
        return base_result
class ByWeatherKindDataLoader(AbstractDataLoader):
    def __init__(self,api_name,weather_kind) -> None:
        super().__init__()
        self.api_name=api_name
        self.weather_kind=weather_kind
    def process_weather_data(self,weather_data,kind):
        pass
    def get_stat_name(self)->str:
        pass
    def load(self) -> List[WeatherGraph]:
        ping_result_kinds = ["min_rtt", "avg_rtt", "max_rtt"]
        result=[]
       
        for kind in ping_result_kinds:
            weather_data=dict()
            for json_obj in self.raw_data:
               
                weather= get_weather_data(json_obj,self.api_name,self.weather_kind)
                if weather!=None:
                    if weather not in weather_data:
                        weather_data[weather]=[]
                    weather_data[weather].append(json_obj["time"])
            self.process_weather_data(weather_data,kind)
            weather_sorted=sorted(weather_data.keys())
            aggregration_methods={"min":np.min,"avg":np.mean,"max":np.max}

            for aggr in aggregration_methods:
                path=f"graphs/weather_{self.get_stat_name()}/{kind}/{aggr}/{self.api_name}_{self.weather_kind}"+EXTENSION
                inf=WeatherGraphInformation(self.weather_kind+"->"+self.get_stat_name(),self.weather_kind +" from "+ self.api_name,self.get_stat_name(),path,"")
                x_values=weather_sorted
                y_values=[aggregration_methods[aggr](weather_data[w]) for w in weather_sorted]
                result.append(WeatherGraph(x_values,[y_values],inf))


        return result
class   ByWeatherKindPingDataLoader(ByWeatherKindDataLoader):
    def get_stat_name(self) -> str:
        return "ping"
    def load(self) -> List[WeatherGraph]:
        return super().load()
    def process_weather_data(self,weather_data,kind):
        for w in weather_data:
            
            for i in range(len(weather_data[w])):
                json_obj=time_jsonObj[weather_data[w][i]]
                ping=json_obj["ping_result"][kind]
                weather_data[w][i]=ping

api_weather_product= list(itertools.product(apis_names,weather_kinds))
loaders=[
    TimePingDataLoader()
]
loaders.extend([TimePingWeatherLoader(x[0],x[1]) for x in api_weather_product])
loaders.extend([ByWeatherKindPingDataLoader(x[0],x[1]) for x in api_weather_product])



def main():
    for loader in loaders:
        loader.load_all_data()
        weather_graphs=loader.load()
        for wg in weather_graphs:
            wg.draw()


if __name__ == "__main__":
    main()
