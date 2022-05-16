import http.client
#from weatherbit.api import Api
import requests
from datetime import datetime
LAAR_LAT=52.5761865151627
LAAR_LON=6.754423961898484
class WeatherInformation:
    def __init__(self) -> None:
        self.temperature:float=0
        self.humidity:float=0
        self.wind_speed:float=0
        self.air_pressure=0
        self.rain=0
        self.thunder=0
        self.time=0
        self.last_updated=0
        self.location=0
        self.sun_set=0
        self.sun_rise=0
        self.description=''

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
    def load_data(lat:float,lon:float)-> WeatherInformation:
        pass
def get_combined_weather_data(apis):
    result={}
    for api_type in apis:
        api=api_type()
        res=api.load_data(LAAR_LAT,LAAR_LON)
        result[api_type.__name__]=res
    return result   
   
    
class WeatherBitIO(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float)-> WeatherInformation:
        apikey = '7d655bb508cd4716b40f67d2cc87878f'
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
    def load_data(self,lat:float, lon:float):
        apikey = '690ba17ef992471e988115539221305'
        url = f'http://api.weatherapi.com/v1/current.json?key={apikey}&q={lat},{lon}'
        response = requests.get(url)
        data = response.json()

        info = WeatherInformation()
        info.temperature = data['current']['temp_c']
        info.humidity = data['current']['humidity']
        info.wind_speed = data['current']['wind_kph']
        info.air_pressure = data['current']['pressure_mb']
        #info.rain=0
        #info.thunder=0
        #info.time = 
        info.last_updated = data['current']['last_updated_epoch']
        #info.location = 
        #info.sun_set = 
        #info.sun_rise =
        info.description = data['current']['condition']['text']

        
        return info
class AccuWeather(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float):
        apikey = 'Uh8LxD0mRtzAjgK7A0BQl6AIz4Dnl9HG'
        url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={apikey}&q={lat},{lon}'
        response = requests.get(url)
        data = response.json()
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
    def load_data(self,lat:float,lon:float):

        apikey = '27a0231c6a206d1fffeba8a2d00e968f'
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
        #info.thunder=0
        #info.time = 
        info.last_updated = data['dt']
        #info.location = 
        info.sun_set = data['sys']['sunset']
        info.sun_rise = data['sys']['sunrise']
        info.description = data['weather'][0]['description']

        return info

   
    
    
       
class BuienRadar(AbstractWeatherAPI):
    # Credit https://www.buienradar.nl
    def distance(self,x1:float,y1:float,x2:float,y2:float):
        dx=x1-x2
        dy=y1-y2
        return dx*dx+dy*dy
    def load_rain_data(self,lat:float,lon:float):
        request_result=requests.request("GET",url=f"https://gpsgadget.buienradar.nl/data/raintext?lat={lat}&lon={lon}")
        precipitation=request_result.content.decode().split("\n")[0].split("|")[0]
        precipitation=int(precipitation)
        if precipitation==0:
            return 0
        return 10**((precipitation-109)/32)
    def load_data(self,lat: float, lon: float) -> WeatherInformation:
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
        result.time=datetime.fromisoformat(best_station["timestamp"])
        result.last_updated=result.time
        result.thunder=None # maybe extactable from description
        result.wind_speed=best_station["windspeed"]
        result.description=best_station["weatherdescription"] # sadly in dutch
        return result
