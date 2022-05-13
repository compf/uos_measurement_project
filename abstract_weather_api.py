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
class AbstractWeatherAPI:
    def loadData()-> WeatherInformation:
        pass