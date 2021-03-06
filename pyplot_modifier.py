#used to change a graph via the bin file
#Hence, not all graphs must be regenerated if one graph must be changed
import json
import matplotlib.pyplot as plt
import os
import pickle5 as pickle
import sys
# if svg file provided, there should be corresponding .bin file, so we replace
if sys.argv[1].endswith(".svg"):
    sys.argv[1]=sys.argv[1].replace(".svg",".bin")
with open(sys.argv[2]) as f:
    json_obj=json.load(f)
with open(sys.argv[1],"rb") as f:
    fig=pickle.load(f)
    x_data=plt.gca().lines[0].get_xdata()
    y_data=plt.gca().lines[0].get_ydata()
    plt.clf()
    plt.figure(figsize=(json_obj["sizex"],json_obj["sizey"]))
    plt.ylabel(json_obj["ylabel"])
    plt.xlabel(json_obj["xlabel"])
    plt.title(json_obj["title"])
   # plt.xlim([json_obj["xmin"],json_obj["xmax"]])
    plt.ylim([json_obj["ymin"],json_obj["ymax"]])
    if json_obj["type"]=="bar":
        plt.bar(x_data,y_data,width=json_obj["barwidth"])
    else:
        plt.plot(x_data,y_data)
    plt.savefig(sys.argv[1].replace(".bin",".svg"))




