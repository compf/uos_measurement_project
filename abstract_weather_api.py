import http.client
#from weatherbit.api import Api
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

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
    def load_data(lat:float,lon:float)-> WeatherInformation:
        pass
def get_combined_weather_data(apis,lat:float,lon:float):
    result={}
    for api_key in apis:
        api_type=apis_dict[api_key]
        api=api_type()
        try:
            res=api.load_data(lat,lon)
            result[api_type.__name__]=res
        except Exception as e:
            print("ignoring exception",e)
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

class Meteomatics(AbstractWeatherAPI):
    def load_data(self,lat:float,lon:float):
        # Valid until 2022-06-08
        api_user = 'vera_dast'
        api_password = '5RF3ecV1f3'
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        url = f'https://api.meteomatics.com/{current_date}/t_2m:C,precip_1h:mm,wind_speed_10m:ms,sunrise:sql,sunset:sql,weather_symbol_1h:idx/{lat},{lon}/json'
        response = requests.get(url, verify=False, auth=HTTPBasicAuth(api_user, api_password))
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
    def load_data(self,lat:float,lon:float):
        # Valid until 2022-06-26
        client_id = 'fNhvFwdyUKxsfowQsQ6rD'
        client_secret = 'MFmQhE0EugSaG8R41jYo4jhUDgbhU7MOG5bhrAE4'

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
    def load_data(self,lat:float,lon:float):
        # Only for Laar !!!!!! lat and lon have no effects
        # Valid until 2022-06-26
        token_url = 'https://pfa.foreca.com/authorize/token'
        log_vars = {'user': 'mymob-12345', 'password': 'NoeHKNYSwaZI'}
        access_token = requests.post(token_url, data=log_vars).json()['access_token']
        authorization_header = {'Authorization': 'Bearer '+access_token}
        current_url = 'https://pfa.foreca.com/api/v1/current/102882115' # 102882115 = Laar's Location ID
        #url2 = 'https://pfa.foreca.com/api/v1/location/search/Laar' # search for location id by name
        response = requests.post(current_url, headers=authorization_header)
        data = response.json()

        info = WeatherInformation()
        info.temperature = data['current']['temperature']
        info.rain        = data['current']['precipProb']
        info.wind_speed  = data['current']['windSpeed']
        info.thunder  = data['current']['thunderProb']
        info.humidity  = data['current']['relHumidity']
        info.last_updated  = data['current']['time']
        info.air_pressure  = data['current']['pressure']
        info.description  = data['current']['symbol'] #https://developer.foreca.com/resources
        
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
    
