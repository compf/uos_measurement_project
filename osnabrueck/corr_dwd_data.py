STATION_ID="0034"
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
temp=pd.read_csv("data/produkt_zehn_min_tu_20201216_20220618_00342.txt",delimiter=";")
wind =pd.read_csv("data/produkt_zehn_min_ff_20201216_20220618_00342.txt",delimiter=";")
rain =pd.read_csv("data/produkt_zehn_min_rr_20201216_20220618_00342.txt",delimiter=";")

temp["MESS_DATUM"]=[datetime.datetime.strptime(str(timeval), "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc).timestamp() for timeval in temp["MESS_DATUM"]]
wind["MESS_DATUM"]=[datetime.datetime.strptime(str(timeval), "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc).timestamp() for timeval in wind["MESS_DATUM"]]
rain["MESS_DATUM"]=[datetime.datetime.strptime(str(timeval), "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc).timestamp() for timeval in rain["MESS_DATUM"]]



rdx1=pd.read_csv("ceragon_RxLevel_7d.txt",delimiter=";",names=["Time","RDX","Ignore"])
rdx2=pd.read_csv("ceragon_RxLevel_7d_2.txt",delimiter=";",names=["Time","RDX","Ignore"])
print(rdx2)
rdx=pd.concat([rdx1,rdx2],ignore_index=True,sort=False)
rdx["RDX"]=-rdx["RDX"]
flag=False
start_time=rdx["Time"][0]
end_time=rdx["Time"][len(rdx["Time"])-1]

i1=temp.MESS_DATUM[temp.MESS_DATUM==start_time].index.tolist()[0]
j1=wind.MESS_DATUM[wind.MESS_DATUM==start_time].index.tolist()[0]
k1=rain.MESS_DATUM[rain.MESS_DATUM==start_time].index.tolist()[0]

i2=temp.MESS_DATUM[temp.MESS_DATUM==end_time].index.tolist()[0]
j2=wind.MESS_DATUM[wind.MESS_DATUM==end_time].index.tolist()[0]
k2=rain.MESS_DATUM[rain.MESS_DATUM==end_time].index.tolist()[0]











print(k2)
temp=temp[i1:i2-1]
rain=rain[j1:j2-1]
wind=wind[k1:k2-1]
print(temp["TT_10"])






labels={"Temperature":(temp,"TT_10"),
"Humidity":(temp,"RF_10"),
"Airpressure":(temp,"PP_10"),
"Rain":(rain,"RWS_10"),
"Wind speed":(wind,"FF_10")


}
plt.figure()
pos=np.arange(5)
width=0.2
values=[]
for l in labels:
    df,col=labels[l]
    x=np.corrcoef(df[col],y=rdx["RDX"])[0][1]
    print(x)
    values.append(x)
    
plt.bar(pos,values,width=0.2,label="RX power")
plt.title("Correlation RX/weather")
plt.ylabel("Correlation")
plt.ylim([-1,1])
plt.grid()
plt.legend()
plt.tight_layout()

#plt.grid()
plt.axhline(y=0,linewidth=1, color='k')
plt.xticks(pos,[l for l in labels])
plt.savefig("osnabrueck_dwd.pdf")
plt.close()
print(x)




