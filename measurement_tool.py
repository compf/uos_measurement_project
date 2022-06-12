import pingparsing
from abstract_weather_api import *
import time
import sys
import json
import jsonpickle
import argparse
import iperf3
LAAR_PING_IP="185.72.203.254"
class PingResult:
    def __init__(self, avg_rtt:float,max_rtt:float,min_rtt:float,loss:float) -> None:
        self.avg_rtt=avg_rtt
        self.max_rtt=max_rtt
        self.min_rtt=min_rtt
        self.loss=loss
def main(args):
    start_time=args.time
    AbstractWeatherAPI.START_TIME=start_time
    with open(args.conf) as f:
        conf_obj=json.load(f)
    print(start_time)
    json_obj={}
    json_obj["time"]=start_time
    json_obj["ip"]=conf_obj["ping_ip"]

    apis=conf_obj["apis"]
    weather=get_combined_weather_data(apis,conf_obj["lat"],conf_obj["lon"],conf_obj)
    
    
    ping_res=ping(conf_obj)
    ping_res=PingResult(ping_res['rtt_avg'],ping_res['rtt_max'],ping_res['rtt_min'],ping_res['packet_loss_rate'])
    get_forecast(json_obj,start_time)
    iperf_result=iperf(conf_obj)
    json_obj["ping_result"]=ping_res.__dict__
    json_obj["iperf_result"]=iperf_result
    json_obj["weather"]=weather
    with open("project_archive/"+str(start_time)+".json","w") as f:
        f.write( jsonpickle.encode(json_obj, unpicklable=False))
def ping(conf_obj):
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = conf_obj["ping_ip"]
    transmitter.count = conf_obj["ping_count"]
    result = transmitter.ping()
    return ping_parser.parse(result).as_dict()
def iperf(conf_obj):
    iperf_ip=conf_obj["iperf_ip"]
    client=iperf3.Client()
    client.duration=conf_obj["iperf_duration"]
    client.server_hostname=iperf_ip
    result=client.run()
    sender_stats=result.json["end"]["streams"][0]["sender"]
    bitrate=sender_stats["bits_per_second"]
    retr=sender_stats["retransmits"]
    return {"bits_per_sec":bitrate,"retransmissions":retr}



def get_forecast(json_obj,start_time):
    json_path=f"project_archive/forecast/{start_time}.json"
    if os.path.exists(json_path):
        with open(json_path,"r") as f:
            json_obj["forecast"]=json.load(f)
        os.unlink(json_path)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--time",type=int,help="The time when the script was started")
    parser.add_argument("--conf",type=str,help="Path to a config file")
    args=parser.parse_args()
    
    main(args)
    #dummy_obj={"iperf_ip":'37.221.197.246',"iperf_duration":10}
    #iperf(dummy_obj)