import http.client
#from weatherbit.api import Api
import requests

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


def main():
    print(AbstractWeatherAPI.get_weatherbit_io(52.283, 8.050))
    print(AbstractWeatherAPI.get_weatherapi_com(52.283, 8.050))
    print(AbstractWeatherAPI.get_accuweather_com(52.283, 8.050))
    print(AbstractWeatherAPI.get_openweathermap_org(52.283, 8.050))
    

class AbstractWeatherAPI:
    def loadData()-> WeatherInformation:
        pass

    def get_weatherbit_io(lat, lon):
        apikey = '7d655bb508cd4716b40f67d2cc87878f'
        url = f"https://api.weatherbit.io/v2.0/current?&lat={lat}&lon={lon}&key={apikey}&include=minutely"
        response = requests.get(url)
        data = response.json()['data'][0]

        info = WeatherInformation()
        info.temperature = data['temp']
        info.humidity = data['rh']
        info.wind_speed = data['wind_spd']
        info.air_pressure = data['pres']
        #info.rain=0
        #info.thunder=0
        #info.time =0
        info.last_updated= data['ts']
        info.location = data['station']
        info.sun_set = data['sunset']
        info.sun_rise = data['sunrise']
        info.description = data['weather']['description']

        return(info)



    def get_weatherapi_com(lat, lon):
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


    def get_accuweather_com(lat, lon):
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
        #info.rain=0
        #info.thunder=0
        #info.time = 
        info.last_updated = data[0]['EpochTime']
        #info.location = 
        #info.sun_set = 
        #info.sun_rise =
        info.description = data[0]['WeatherText']

        return info

    def get_openweathermap_org(lat, lon):
        apikey = '27a0231c6a206d1fffeba8a2d00e968f'
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&units=metric'
        response = requests.get(url)
        data = response.json()
 
        info = WeatherInformation()
        info.temperature = data['main']['temp']
        info.humidity = data['main']['humidity']
        info.wind_speed = data['wind']['speed']
        info.air_pressure = data['main']['pressure']
        if 'rain' in data:
            info.rain = data['rain']['1h']
        #info.thunder=0
        #info.time = 
        info.last_updated = data['dt']
        #info.location = 
        info.sun_set = data['sys']['sunset']
        info.sun_rise = data['sys']['sunrise']
        info.description = data['weather'][0]['description']

        return info

if __name__=="__main__":
    main()