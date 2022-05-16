from  pythonping import ping
from abstract_weather_api import *
import time
import sys
import json
import jsonpickle
PING_IP="185.72.203.254"
class PingResult:
    def __init__(self, avg_rtt:float,max_rtt:float,min_rtt:float,loss:float) -> None:
        self.avg_rtt=avg_rtt
        self.max_rtt=max_rtt
        self.min_rtt=min_rtt
        self.loss=loss
def main():
    start_time=int(sys.argv[1])
    print(start_time)
    json_obj={}
    json_obj["time"]=start_time
    json_obj["ip"]=PING_IP
    apis=[WeatherBitIO,WeatherAPI,AccuWeather,OpenWeatherMap,BuienRadar]
    weather=get_combined_weather_data(apis)
    res= ping(PING_IP,verbose=False,count=10)
    ping_res=PingResult(res.rtt_avg_ms,res.rtt_max_ms,res.rtt_min_ms,res.packet_loss)
    json_obj["ping_result"]=ping_res
    json_obj["weather"]=weather
    with open("project_archive/"+str(start_time)+".json","w") as f:
        f.write( jsonpickle.encode(json_obj, unpicklable=False))

if __name__=="__main__":
    main()