import requests

from abstract_weather_api import WeatherInformation, AbstractWeatherAPI


class WesterbergWetter(AbstractWeatherAPI):
    def load_data(self, lat: float, lon: float) -> WeatherInformation:
        # https://www.westerbergwetter.de/
        # Only for Wetterstation Osnabrück-Westerberg !!!!!!
        html_data = requests.request("GET", url="https://www.westerbergwetter.de/")

        info = WeatherInformation()
        info.temperature =  html_data.text.split(">Temperatur")[1].split("&deg;C")[0].strip()
        info.humidity = html_data.text.split(">&nbsp;Feuchte      </b>")[1].split("%<br>")[0].strip()
        info.wind_speed = html_data.text.split("&nbsp;Wind      </b>")[1].split("km/h")[0].strip()
        info.air_pressure = html_data.text.split("&nbsp;Luftdruck      </b>")[1].split("hPa")[0].strip()
        info.rain = html_data.text.split("Heute fiel bisher")[1].split(" mm Niederschlag")[0].strip()
        return (info)

def main():
    wb = WesterbergWetter()
    print(wb.load_data(0,0))


if __name__ == "__main__":
    main()

