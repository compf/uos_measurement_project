from  pythonping import ping
class PingResult:
    def __init__(self, avg_rtt:float,max_rtt:float,min_rtt:float,loss:float) -> None:
        self.avg_rtt=avg_rtt
        self.max_rtt=max_rtt
        self.min_rtt=min_rtt
        self.loss=loss
def main():


   res= ping("8.8.8.8",verbose=False,count=10)
   ping_res=PingResult(res.rtt_avg_ms,res.rtt_max_ms,res.rtt_min_ms,res.packet_loss)
   print(ping_res.avg_rtt,ping_res.loss)

if __name__=="__main__":
    main()