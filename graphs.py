import os
import json
from typing import Tuple, List
import itertools
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import abstract_weather_api
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
            ax.plot(pair[0],label=pair[1],color=colors[counter])
    
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
        global raw_json_data
        if raw_json_data == None:
            self.raw_data = []
            for fname in os.listdir("project_archive"):
                if fname=="forecast":
                    continue
                with open("project_archive/"+fname) as f:
                    self.raw_data.append(json.load(f))
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
            res.information.path=f"graphs/time_ping/weather/{self.api_name}_{self.weather_kind}_{res.information.kind}"+EXTENSION
            y_values=res.y_values[1]
            res.information.kind+=f"_{self.api_name}_{self.weather_kind}"
            for json_obj in self.raw_data:
                if self.api_name in json_obj["weather"] and   json_obj["weather"][self.api_name]!=None  and self.weather_kind in json_obj["weather"][self.api_name]:
                    v=json_obj["weather"][self.api_name][self.weather_kind]
                    y_values.append(v)
                else:
                   
                    y_values.append(INVALID)
        return base_result
                
loaders=[
    TimePingDataLoader()
]
loaders.extend([TimePingWeatherLoader(x[0],x[1]) for x in itertools.product(apis_names,weather_kinds)])
def main():
    for loader in loaders:
        loader.load_all_data()
        weather_graphs=loader.load()
        for wg in weather_graphs:
            wg.draw()


if __name__ == "__main__":
    main()
