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
class TimeThroughputDataLoader(AbstractDataLoader):
    def load(self) -> List[WeatherGraph]:
        x_data=[]
        y_data=[]
        path=f"graphs/time_throughput.svg"
        inf=WeatherGraphInformation("Time => Throughput","Time [s]",["Throughput [bit/s]"],path,"")
        for json_obj in self.raw_data:
            if "iperf_result" in json_obj:
                x_data.append(json_obj["time"])
            
                y_data.append(json_obj["iperf_result"]["bits_per_sec"])
        return [WeatherGraph(x_data,[y_data],inf)]
class TimeRetransmissionDataLoader(AbstractDataLoader):
    def load(self) -> List[WeatherGraph]:
        x_data=[]
        y_data=[]
        path=f"graphs/time_retransmission.svg"
        inf=WeatherGraphInformation("Time => Retransmission","Time [s]",["Retransmissions"],path,"")
        for json_obj in self.raw_data:
            if "iperf_result" in json_obj:
                x_data.append(json_obj["time"])
            
                y_data.append(json_obj["iperf_result"]["retransmissions"])
        return [WeatherGraph(x_data,[y_data],inf)]

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
class TimeThroughputWeatherLoader(TimeThroughputDataLoader):
    def __init__(self,api_name,weather_kind) -> None:
        super().__init__()
        self.api_name=api_name
        self.weather_kind=weather_kind
    def load(self) -> List[WeatherGraph]:
        base_result= super().load()
        for res in base_result:
            res.information.y_labels.append(self.weather_kind +" from "+self.api_name)
            res.y_values.append([])
            res.information.path=f"graphs/time_throughput/{self.api_name}_{self.weather_kind}"+EXTENSION
            y_values=res.y_values[1]
            res.information.kind+=f"_{self.api_name}_{self.weather_kind}"
            for json_obj in self.raw_data:
                if"iperf_result" not in  json_obj:
                    continue

                weather=get_weather_data(json_obj,self.api_name,self.weather_kind)
                if weather!=None:
                    y_values.append(weather)
                else:
                   
                    y_values.append(INVALID)
        return base_result
class TimeRetransmissionsWeatherLoader(TimeRetransmissionDataLoader):
    def __init__(self,api_name,weather_kind) -> None:
        super().__init__()
        self.api_name=api_name
        self.weather_kind=weather_kind
    def load(self) -> List[WeatherGraph]:
        base_result= super().load()
        for res in base_result:
            res.information.y_labels.append(self.weather_kind +" from "+self.api_name)
            res.y_values.append([])
            res.information.path=f"graphs/time_retransmissions/{self.api_name}_{self.weather_kind}"+EXTENSION
            y_values=res.y_values[1]
            res.information.kind+=f"_{self.api_name}_{self.weather_kind}"
            for json_obj in self.raw_data:
                if"iperf_result" not in  json_obj:
                    continue

                weather=get_weather_data(json_obj,self.api_name,self.weather_kind)
                if weather!=None:
                    y_values.append(weather)
                else:
                   
                    y_values.append(INVALID)
        return base_result
class ByWeatherKindDataLoader(AbstractDataLoader):
    def __init__(self,api_name,weather_kind,measurement_result_kinds,timespan) -> None:
        super().__init__()
        self.measurement_result_kinds=measurement_result_kinds
        self.api_name=api_name
        self.weather_kind=weather_kind
        self.timespan=timespan
    def process_weather_data(self,weather_data,kind):
        pass
    def get_stat_name(self)->str:
        pass
    def is_time_ok(self,t,json_obj):
        if "OpenWeatherMap" not in  json_obj["weather"]:
            dt=datetime.fromtimestamp(t)
            
            hour=5
            minute=30
            #hour,minute=json_obj["weather"]["WeatherBitIO"]["sun_set"].split(":")
            dt=datetime(dt.year,dt.month,dt.day,int(hour),int(minute),dt.second)
          
            sun_rise=dt.timestamp()
            #hour,minute=json_obj["weather"]["WeatherBitIO"]["sun_rise"].split(":")
            # defining sunset only when it is clearly dark because 19:00 it is still too light
            # still need to find better time
            hour=23
            minute=59
            dt=datetime(dt.year,dt.month,dt.day,int(hour),int(minute),dt.second)

            sun_set=dt.timestamp()
        else:
            sun_set=json_obj["weather"]["OpenWeatherMap"]["sun_set"]
            sun_rise=json_obj["weather"]["OpenWeatherMap"]["sun_rise"]
        if self.timespan==Timespan.DAY:
            return t>= sun_rise and t<=sun_set
        elif self.timespan== Timespan.NIGHT:
            return t<sun_rise or t>sun_set
        else: 
            return True
    def load(self) -> List[WeatherGraph]:
        result=[]
       
        for kind in self.measurement_result_kinds:
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
class Timespan:
    ALL=0
    DAY=1
    NIGHT=2
class   ByWeatherKindPingDataLoader(ByWeatherKindDataLoader):
    def get_stat_name(self) -> str:
        if self.timespan==Timespan.ALL:
            return "ping"
        elif self.timespan==Timespan.DAY:
            return "ping_day"
        else:
            return "ping_night"
    def load(self) -> List[WeatherGraph]:
        return super().load()
    def process_weather_data(self,weather_data,kind):
        remove=[]
        for w in weather_data:
            res=[]
            for t in weather_data[w]:
                json_obj=time_jsonObj[t]
                if self.is_time_ok(t,json_obj):
                    ping=json_obj["ping_result"][kind]
                    res.append(ping)
            weather_data[w]=res
            if len(res)==0:
                remove.append(w)
        for r in remove:
            weather_data.pop(r,None)
class ByWeatherKindThroughput(ByWeatherKindDataLoader):
    def get_stat_name(self) -> str:
        if self.timespan==Timespan.ALL:
            return "Throughput"
        elif self.timespan==Timespan.DAY:
            return "Throughput_day"
        else:
            return "Throughput_night"
    def process_weather_data(self, weather_data, kind):
        remove=[]
        for w in weather_data:
            res=[]
            for t in weather_data[w]:
                json_obj=time_jsonObj[t]
                if self.is_time_ok(t,json_obj) and "iperf_result" in json_obj :
                    ping=json_obj["iperf_result"]["bits_per_sec"]
                    res.append(ping)
            weather_data[w]=res
            if len(res)==0:
                remove.append(w)
        for r in remove:
            weather_data.pop(r,None)
class ByWeatherKindRetransmission(ByWeatherKindDataLoader):
    def get_stat_name(self) -> str:
        if self.timespan==Timespan.ALL:
            return "Retransmission"
        elif self.timespan==Timespan.DAY:
            return "Retransmission_day"
        else:
            return "Retransmission_night"
    def process_weather_data(self, weather_data, kind):
        remove=[]
        for w in weather_data:
            res=[]
            for t in weather_data[w]:
                json_obj=time_jsonObj[t]
                if self.is_time_ok(t,json_obj) and "iperf_result" in json_obj :
                    ping=json_obj["iperf_result"]["retransmissions"]
                    res.append(ping)
            weather_data[w]=res
            if len(res)==0:
                remove.append(w)
        for r in remove:
            weather_data.pop(r,None)

api_weather_product= list(itertools.product(apis_names,weather_kinds))
ping_result_kinds=["min_rtt", "avg_rtt", "max_rtt"]
loaders=[
    TimePingDataLoader(),
    TimeThroughputDataLoader(),
    TimeRetransmissionDataLoader()
]

loaders.extend([TimePingWeatherLoader(x[0],x[1]) for x in api_weather_product])
loaders.extend([TimeThroughputWeatherLoader(x[0],x[1]) for x in api_weather_product])
loaders.extend([TimeRetransmissionsWeatherLoader(x[0],x[1]) for x in api_weather_product])

loaders.extend([ByWeatherKindPingDataLoader(x[0],x[1],ping_result_kinds,Timespan.ALL) for x in api_weather_product])
loaders.extend([ByWeatherKindPingDataLoader(x[0],x[1],ping_result_kinds,Timespan.DAY) for x in api_weather_product])
loaders.extend([ByWeatherKindPingDataLoader(x[0],x[1],ping_result_kinds,Timespan.NIGHT) for x in api_weather_product])

loaders.extend([ByWeatherKindThroughput(x[0],x[1],["all"],Timespan.ALL) for x in api_weather_product])
loaders.extend([ByWeatherKindThroughput(x[0],x[1],["all"],Timespan.DAY) for x in api_weather_product])
loaders.extend([ByWeatherKindThroughput(x[0],x[1],["all"],Timespan.NIGHT) for x in api_weather_product])

loaders.extend([ByWeatherKindRetransmission(x[0],x[1],["all"],Timespan.ALL) for x in api_weather_product])
loaders.extend([ByWeatherKindRetransmission(x[0],x[1],["all"],Timespan.DAY) for x in api_weather_product])
loaders.extend([ByWeatherKindRetransmission(x[0],x[1],["all"],Timespan.NIGHT) for x in api_weather_product])


def main():
    for loader in loaders:
        loader.load_all_data()
        weather_graphs=loader.load()
        for wg in weather_graphs:
            wg.draw()


if __name__ == "__main__":
    main()
