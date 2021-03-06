#here  is all the logic for downloading the weather api data
import http.client
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime,timedelta
import os,time
import json
class WeatherInformation:
    def __init__(self) -> None:
        self.temperature:float=None
        self.humidity:float=None
        self.wind_speed:float=None
        self.air_pressure=None
        self.rain=None
        self.thunder=None
        self.time=None
        self.last_updated=None
        self.location=None
        self.sun_set=None
        self.sun_rise=None
        self.description=None

    def __str__(self):
        return ("WeatherInformation: \n temperature : " + str(self.temperature) + 
        "\n humidity : " + str(self.humidity) +
        "\n wind_speed : " + str(self.wind_speed) +
        "\n air_pressure : " + str(self.air_pressure) +
        "\n rain : " + str(self.rain) +
        "\n thunder : " + str(self.thunder) +
        "\n time : " + str(self.time) +
        "\n last_updated : " + str(self.last_updated) +
        "\n location : " + str(self.location) +
        "\n sun_set : " + str(self.sun_set) +
        "\n sun_rise : " + str(self.sun_rise) +
        "\n description : " + str(self.description)
        )

class AbstractWeatherAPI:
    def get_apis_data(self,conf,typ):
        return conf["apis_data"][apis_dict_reversed[typ]]  
    def load_data(lat:float,lon:float)-> WeatherInformation:
        pass
    def save_forecast(self,info:WeatherInformation,api_key_dict:str):
        out_path=f"project_archive/forecast/{info.time}.json"
        if os.path.exists(out_path):
            with open(out_path,"r") as f:
                json_obj=json.load(f)
            json_obj[api_key_dict]=info.__dict__
            with open(out_path,"w") as f:
                json.dump(json_obj,f)
        else:
            json_obj={}
            json_obj[api_key_dict]=info.__dict__
            with open(out_path,"w") as f:
                json.dump(json_obj,f)


def get_combined_weather_data(apis,lat:float,lon:float,conf):
    result={}
    for api_key in apis:
        api_type=apis_dict[api_key]
        api=api_type()
        try:
            res=api.load_data(lat,lon,conf).__dict__
            result[api_type.__name__]=res
        except Exception as e:
            print("ignoring exception at ",api_key,e)
    return result 

   
    
class WeatherBitIO(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float,conf)-> WeatherInformation:
        apikey = self.get_apis_data(conf,WeatherBitIO)
        url = f"https://api.weatherbit.io/v2.0/current?&lat={lat}&lon={lon}&key={apikey}&include=minutely"
        response = requests.get(url)
        data = response.json()['data'][0]

        info = WeatherInformation()
        info.temperature = data['temp']
        info.humidity = data['rh']
        info.wind_speed = data['wind_spd']
        info.air_pressure = data['pres']
        info.rain=data["precip"]
        #info.thunder=0
        #info.time =0
        info.last_updated= data['ts']
        info.location = data['station']
        info.sun_set = data['sunset']
        info.sun_rise = data['sunrise']
        info.description = data['weather']['description']

        return(info)
class WeatherAPI(AbstractWeatherAPI):
    def load_data(self,lat:float, lon:float,conf):
        apikey = self.get_apis_data(conf,WeatherAPI)
        url = f'http://api.weatherapi.com/v1/forecast.json?key={apikey}&q={lat},{lon}'
        response = requests.get(url)
        data = response.json()

        info = WeatherInformation()
        info.temperature = data['current']['temp_c']
        info.humidity = data['current']['humidity']
        info.wind_speed = data['current']['wind_kph']
        info.air_pressure = data['current']['pressure_mb']
        info.rain= data['current']['precip_mm']
        info.last_updated = data['current']['last_updated_epoch']
       
        info.description = data['current']['condition']['text']

        self.forecast(data)
        return info
    def forecast(self,data):
        curr_time=time.time()-6*60*60
       
        hour=data["forecast"]["forecastday"][0]["hour"]
        hour=min([h for h in hour if h['time_epoch']> curr_time ],key=lambda x:x["time_epoch"])
        info=WeatherInformation()
        info.temperature = hour['temp_c']
        info.humidity = data['current']['humidity']
        info.wind_speed = hour['wind_kph']
        info.air_pressure = hour['pressure_mb']
        info.rain= hour['precip_mm']
        info.time = hour['time_epoch']

        info.description = hour['condition']['text']
        self.save_forecast(info,apis_dict_reversed[WeatherAPI])

class AccuWeather(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float,conf):
        apikey = self.get_apis_data(conf,AccuWeather)
        url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={apikey}&q={lat},{lon}'
        response = requests.get(url)
        data = response.json()
        if "key" not in data:
            return None
        location_key = data['Key']

        url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={apikey}&q={lat},{lon}&details=true'
        response = requests.get(url)
        data = response.json()

        info = WeatherInformation()
        info.temperature = data[0]['Temperature']['Metric']['Value']
        info.humidity = data[0]['RelativeHumidity']
        info.wind_speed = data[0]['Wind']['Speed']['Metric']['Value']
        info.air_pressure = data[0]['Pressure']['Metric']['Value']
        info.rain=data[0]["HasPrecipitation"] #sadly no information about strength of rain
        #info.thunder=0
        #info.time = 
        info.last_updated = data[0]['EpochTime']
        #info.location = 
        #info.sun_set = 
        #info.sun_rise =
        info.description = data[0]['WeatherText']

        return info
class OpenWeatherMap(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float,conf):

        apikey = self.get_apis_data(conf,OpenWeatherMap)
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&units=metric'
        response = requests.get(url)
        data = response.json()
 
        info = WeatherInformation()
        info.temperature = data['main']['temp']
        info.humidity = data['main']['humidity']
        info.wind_speed = data['wind']['speed']
        info.air_pressure = data['main']['pressure']
        if "precipitation" in data:
            info.rain = data['precipitation']['value']
        else:
            info.rain=0

        info.last_updated = data['dt']
        info.sun_set = data['sys']['sunset']
        info.sun_rise = data['sys']['sunrise']
        info.description = data['weather'][0]['description']
        self.forecast(apikey,lat,lon)
        return info
    def forecast(self,apikey:str,lat:float,lon:float):
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&units=metric'
        response = requests.get(url)
        curr_time=time.time()
        data = response.json()
        info=WeatherInformation()
        data=min([h for h in data["list"] if h['dt']> curr_time ],key=lambda x:x["dt"])
        info.temperature = data['main']['temp']
        info.time=data["dt"]
        info.humidity = data['main']['humidity']
        info.wind_speed = data['wind']['speed']
        info.air_pressure = data['main']['pressure']
        if "precipitation" in data:
            info.rain = data['precipitation']['value']
        else:
            info.rain=0
        info.description = data['weather'][0]['description']
        self.save_forecast(info,apis_dict_reversed[OpenWeatherMap])




   
    
    
       
class BuienRadar(AbstractWeatherAPI):
    # Credit https://www.buienradar.nl
    def distance(self,x1:float,y1:float,x2:float,y2:float):
        dx=x1-x2
        dy=y1-y2
        return dx*dx+dy*dy
    def load_rain_data(self,lat:float,lon:float):
        request_result=requests.request("GET",url=f"https://gpsgadget.buienradar.nl/data/raintext?lat={lat}&lon={lon}")
        lines=request_result.content.decode().split("\n")
        precipitation=lines[0].split("|")[0]
        precipitation=int(precipitation)
        
        dt=AbstractWeatherAPI.START_TIME
        for line in lines[1:-1]:
            dt+=60*5
            info=WeatherInformation()
            rain=float(line.split("|")[0])
            info.rain=self.convert_precipation(rain)
            info.time=dt
        
            self.save_forecast(info,apis_dict_reversed[BuienRadar])
       
        return self.convert_precipation(precipitation)
    def convert_precipation(self,val:float):
        if val==0:
            return 0
        return 10**((val-109)/32)
    def load_data(self,lat: float, lon: float,conf) -> WeatherInformation:
        CLOSEST_STATION=6279 # maybe lookign for closer one, if tehre is one
        data=requests.request("GET",url="https://data.buienradar.nl/2.0/feed/json")
        json_obj=data.json()
        best_station=min([(self.distance(lat,lon,obj["lat"],obj["lon"]),obj) for obj in json_obj["actual"]["stationmeasurements"]])
        best_station=best_station[1]

        result=WeatherInformation()
        result.air_pressure=best_station["airpressure"]
        result.temperature=best_station["temperature"]
        result.humidity=best_station["humidity"]
        result.location=(lat,lon)
        #result.rain=best_station["precipitation"] # still need to agree on a common format to describe things like
        result.rain=self.load_rain_data(lat,lon)
        result.sun_rise=json_obj["actual"]["sunrise"]
        result.sun_set=json_obj["actual"]["sunset"]
        result.time=datetime.fromisoformat(best_station["timestamp"]).timestamp()
        result.last_updated=result.time
        result.thunder=None # maybe extactable from description
        result.wind_speed=best_station["windspeed"]
        result.description=best_station["weatherdescription"] # sadly in dutch
        return result

class Meteomatics(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float,conf):
        # Valid until 2022-06-08
        api_data=self.get_apis_data(conf,Meteomatics)
        api_user = api_data["api_user"]
        api_password = api_data["api_password"]
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        url = f'https://api.meteomatics.com/{current_date}/t_2m:C,precip_1h:mm,wind_speed_10m:ms,sunrise:sql,sunset:sql,weather_symbol_1h:idx/{lat},{lon}/json'
        response = requests.get(url, verify=True, auth=HTTPBasicAuth(api_user, api_password))
        data = response.json()
        info = WeatherInformation()
        info.temperature = data['data'][0]['coordinates'][0]['dates'][0]['value']
        info.rain        = data['data'][1]['coordinates'][0]['dates'][0]['value']
        info.wind_speed  = data['data'][2]['coordinates'][0]['dates'][0]['value']
        info.sun_rise  = data['data'][3]['coordinates'][0]['dates'][0]['value']
        info.sun_set  = data['data'][4]['coordinates'][0]['dates'][0]['value']
        info.description  = data['data'][5]['coordinates'][0]['dates'][0]['value']
        
        return info

class Aeris(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float,conf):
        api_data=self.get_apis_data(conf,Aeris)
        # Valid until 2022-06-26
        client_id = api_data["client_id"]
        client_secret = api_data["client_secret"]

        url = f'https://api.aerisapi.com/conditions/{lat},{lon}?client_id={client_id}&client_secret={client_secret}'
        response = requests.get(url)
        data = response.json()
        
        info = WeatherInformation()
        info.temperature = data['response'][0]['periods'][0]['tempC']
        info.rain        = data['response'][0]['periods'][0]['precipMM']
        info.wind_speed  = data['response'][0]['periods'][0]['windSpeedKPH']
        info.humidity  = data['response'][0]['periods'][0]['humidity']
        info.last_updated  = data['response'][0]['periods'][0]['timestamp']
        info.air_pressure  = data['response'][0]['periods'][0]['pressureMB']
        info.description  = data['response'][0]['periods'][0]['weatherPrimary']        
        return info
class Foreca(AbstractWeatherAPI):
    def forecast(self,conf):
        api_data=self.get_apis_data(conf,Foreca)
        # Only for Laar !!!!!! lat and lon have no effects
        # Valid until 2022-06-26
        token_url = 'https://pfa.foreca.com/authorize/token'
        log_vars = {'user': api_data["user"], 'password': api_data["password"]}
        access_token = requests.post(token_url, data=log_vars).json()['access_token']
        authorization_header = {'Authorization': 'Bearer '+access_token}
        current_url = f'https://pfa.foreca.com/api/v1/forecast/15minutely/{api_data["location_id"]}?dataset=full'
        response = requests.post(current_url, headers=authorization_header)
        data = response.json()
        for w in data["forecast"]:
            info = WeatherInformation()
            info.temperature = w['temperature']
            info.rain        = w['precipRate']
            info.wind_speed  = w['windSpeed']
            info.thunder  = w['thunderProb']
            info.humidity  = w['relHumidity']
            info.time=int(datetime.fromisoformat(w["time"]).timestamp())
            info.air_pressure  = w['pressure']
            info.description  = w['symbol'] #https://developer.foreca.com/resources
            self.save_forecast(info,apis_dict_reversed[Foreca])


    def load_data(self,lat:float,lon:float,conf):
        api_data=self.get_apis_data(conf,Foreca)
        # Only for Laar !!!!!! lat and lon have no effects
        # Valid until 2022-06-26
        token_url = 'https://pfa.foreca.com/authorize/token'
        log_vars = {'user': api_data["user"], 'password': api_data["password"]}
        access_token = requests.post(token_url, data=log_vars).json()['access_token']
        authorization_header = {'Authorization': 'Bearer '+access_token}
        current_url = f'https://pfa.foreca.com/api/v1/current/{api_data["location_id"]}'
        #url2 = 'https://pfa.foreca.com/api/v1/location/search/Laar' # search for location id by name
        response = requests.post(current_url, headers=authorization_header)
        data = response.json()

        info = WeatherInformation()
        info.temperature = data['current']['temperature']
        info.rain        = data['current']['precipRate']
        info.wind_speed  = data['current']['windSpeed']
        info.thunder  = data['current']['thunderProb']
        info.humidity  = data['current']['relHumidity']
        info.last_updated  = data['current']['time']
        info.air_pressure  = data['current']['pressure']
        info.description  = data['current']['symbol'] #https://developer.foreca.com/resources
        self.forecast(conf)
        return info


apis_dict={
    "buienradar":BuienRadar,
    "openweatherMap":OpenWeatherMap,
    "accuWeather":AccuWeather,
    "weatherAPI":WeatherAPI,
    "weatherBit":WeatherBitIO,
    "meteomatics":Meteomatics,
    "aeris":Aeris,
    "foreca":Foreca
}
apis_dict_reversed=dict([(v,k) for k,v in apis_dict.items()])
    
