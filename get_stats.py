import os
import json
import matplotlib.pyplot as plt
def main():
    rtt_time=[]
    rain_rtt=[]
    temperature_rtt=[]
    for p in os.listdir("project_archive"):
        with open("project_archive/"+p) as f:
            json_obj=json.load(f)
            measurement_time=json_obj["time"]
            max_rtt=json_obj["ping_result"]["max_rtt"]
            rtt_time.append((max_rtt,measurement_time))
            rain_rtt.append((json_obj["weather"]["BuienRadar"]["rain"],max_rtt))
            temperature_rtt.append((json_obj["weather"]["BuienRadar"]["humidity"],max_rtt))

    longest_rtt=sorted(rtt_time,reverse=True)
    #print(longest_rtt)
    
    most_rain=sorted(rain_rtt)
    most_rain=sorted(temperature_rtt)
    #print(most_rain)
    plt.figure()
    temperature=[r[0] for r in most_rain]
    rtt=[r[1] for r in most_rain]

    plt.plot(temperature,rtt)
    #rtt=
    plt.show()
if __name__=="__main__":
    main()
