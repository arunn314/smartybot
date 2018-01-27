import pyowm
from config import OWM_API

class WeatherHandler(object):
    def get_temperature(self, city, country='US'):
        owm = pyowm.OWM(OWM_API)
        place = city + ',' + country
        obs = owm.weather_at_place(place)
        w = obs.get_weather()
        res = w.get_temperature(unit='fahrenheit')
        res['status'] = w.get_detailed_status()
        return self._format_result(city, res['temp'], res['status'])

    def _format_result(self, city, temperature, status):
        response = ('Weather at {city} is {status}. Temperature '
                    'is {temp} F.')
        response = response.format(
            city=city.title(), temp=int(temperature), status=status)
        return response
