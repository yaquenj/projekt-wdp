import requests
import json
import os
from .format_url import format_url
from .config_manager import readConfig
from datetime import datetime, timedelta

forecast_api_url = 'https://api.open-meteo.com/v1/forecast'
geocoding_api_url = 'https://geocoding-api.open-meteo.com/v1/search'

headers = {
    'Content-Type': 'application/json'
}

# kody pogody z jsona
def _load_weather_codes():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'weather-codes.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            weather_codes_list = json.load(f)
        
        # lista -> dict dla ułatwienia
        weather_codes_dict = {}
        for item in weather_codes_list:
            code = int(item['code'])
            weather_codes_dict[code] = {
                'description': item['description'],
                'image': item['image']
            }
        
        return weather_codes_dict
    except Exception as e:
        print(f"Błąd podczas ładowania kodów pogodowych: {e}")
        return {}


WEATHER_CODES = _load_weather_codes()


def getWeather(coordinates):
    try:
        lat, lon = coordinates
        config = readConfig()
        unit = config["preferences"]["unit"]
        temp_unit = "fahrenheit" if unit == "imperial" else "celsius"
        wind_unit = "mph" if unit == "imperial" else "kmh"

        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'temperature_2m,apparent_temperature,dew_point_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,visibility',
            'daily': 'weather_code',
            'temperature_unit': temp_unit,
            'wind_speed_unit': wind_unit,
            'timezone': 'auto',
            'forecast_days': 2  # Dziś + jutro
        }
        
        url = format_url(forecast_api_url)
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status() # handluje errory api

        data = response.json()
        
        weather_list = []
        
        if 'hourly' in data and data['hourly']:
            hourly = data['hourly']
            daily = data.get('daily', {})
            
            # dzisiaj - pobiera dane z aktualnej godziny
            current_hour = datetime.now().hour
            today_data = {
                'description': _get_weather_description(daily.get('weather_code', [0])[0]),
                'temperature': _round(hourly.get('temperature_2m', [None])[current_hour]),
                'apparent_temperature': _round(hourly.get('apparent_temperature', [None])[current_hour]),
                'dew_point': _round(hourly.get('dew_point_2m', [None])[current_hour]),
                'humidity': _round(hourly.get('relative_humidity_2m', [None])[current_hour]),
                'wind_speed': _round(hourly.get('wind_speed_10m', [None])[current_hour]),
                'pressure': _convert_pressure(_round(hourly.get('surface_pressure', [None])[current_hour]), unit),
                'visibility': _convert_visibility(_round(hourly.get('visibility', [None])[current_hour]), unit),
                'image_code': get_weather_image_code(daily.get('weather_code', [0])[0])
            }
            weather_list.append(today_data)
            
            # jutro - srednia z dnia od 10 do 18
            if len(hourly.get('temperature_2m', [])) > 24 + 14:  # czy mamy dane na jutro?
                tomorrow_start = 24 + 10  # jutro 10:00
                tomorrow_end = 24 + 18    # jutro 18:00
                # czemu tak? api zwraca nam zmiany pogody co godzine, jesli jest wiecej niz 24 + 18 elementów w tabeli to znaczy ze mamy dane na jutro, a 24 + 18 to po prostu
                """
                Przykładowe dane z API:
                {'time': ['2025-11-03T00:00', '2025-11-03T01:00', '2025-11-03T02:00', '2025-11-03T03:00', '2025-11-03T04:00', '2025-11-03T05:00', '2025-11-03T06:00', '2025-11-03T07:00', '2025-11-03T08:00', '2025-11-03T09:00', '2025-11-03T10:00', '2025-11-03T11:00', '2025-11-03T12:00', '2025-11-03T13:00', '2025-11-03T14:00', '2025-11-03T15:00', '2025-11-03T16:00', '2025-11-03T17:00', '2025-11-03T18:00', '2025-11-03T19:00', '2025-11-03T20:00', '2025-11-03T21:00', '2025-11-03T22:00', '2025-11-03T23:00', '2025-11-04T00:00', '2025-11-04T01:00', '2025-11-04T02:00', '2025-11-04T03:00', '2025-11-04T04:00', '2025-11-04T05:00', '2025-11-04T06:00', '2025-11-04T07:00', '2025-11-04T08:00', '2025-11-04T09:00', '2025-11-04T10:00', '2025-11-04T11:00', '2025-11-04T12:00', '2025-11-04T13:00', '2025-11-04T14:00', '2025-11-04T15:00', '2025-11-04T16:00', '2025-11-04T17:00', '2025-11-04T18:00', '2025-11-04T19:00', '2025-11-04T20:00', '2025-11-04T21:00', '2025-11-04T22:00', '2025-11-04T23:00'], 'temperature_2m': [7.9, 8.4, 8.2, 7.0, 6.0, 5.4, 4.8, 4.4, 4.7, 6.4, 8.2, 9.5, 10.3, 11.6, 11.8, 11.6, 11.2, 10.6, 9.9, 9.7, 9.4, 9.0, 9.5, 9.3, 8.8, 8.4, 8.7, 9.0, 9.0, 8.6, 8.3, 8.2, 8.0, 8.4, 9.5, 10.9, 12.3, 13.5, 14.0, 14.2, 13.8, 11.8, 10.2, 9.5, 9.0, 8.7, 8.0, 7.6], 'apparent_temperature': [6.0, 6.4, 6.2, 5.1, 3.5, 3.0, 2.5, 2.0, 2.3, 3.4, 5.2, 6.5, 7.3, 8.8, 8.7, 8.4, 8.1, 8.3, 8.1, 7.6, 7.5, 7.3, 7.7, 7.4, 7.0, 6.5, 6.7, 7.0, 7.1, 6.7, 6.4, 6.3, 6.2, 6.4, 7.3, 8.7, 10.3, 11.6, 12.3, 12.6, 12.8, 11.2, 9.3, 8.2, 7.6, 7.3, 6.7, 6.3], 'dew_point_2m': [7.2, 7.9, 7.5, 6.3, 5.3, 4.7, 4.2, 4.0, 4.3, 5.5, 6.4, 6.9, 7.4, 7.4, 7.1, 7.0, 6.8, 7.3, 7.4, 7.3, 7.3, 7.1, 7.8, 7.8, 7.8, 7.5, 7.9, 8.1, 8.0, 7.7, 7.5, 7.3, 7.0, 6.7, 7.0, 7.2, 7.8, 7.9, 7.8, 8.2, 9.2, 9.6, 8.8, 8.1, 7.5, 7.0, 6.2, 5.8], 'relative_humidity_2m': [95, 97, 95, 95, 95, 95, 96, 97, 97, 94, 88, 84, 82, 75, 73, 73, 74, 80, 84, 85, 87, 88, 89, 90, 93, 94, 95, 94, 93, 94, 95, 94, 93, 89, 84, 78, 74, 69, 66, 67, 74, 86, 91, 91, 90, 89, 88, 88], 'wind_speed_10m': [8.7, 10.1, 9.9, 7.0, 9.4, 8.0, 6.1, 6.4, 7.1, 12.8, 14.4, 14.8, 15.8, 15.1, 16.1, 16.9, 15.9, 10.9, 8.3, 10.1, 8.4, 6.5, 8.4, 9.4, 8.7, 9.2, 10.2, 10.3, 10.0, 9.1, 8.7, 8.0, 7.2, 8.4, 9.8, 10.1, 10.0, 9.5, 8.3, 7.6, 5.6, 3.6, 4.3, 5.2, 5.7, 4.1, 2.5, 1.8], 'surface_pressure': [1001.6, 1001.9, 1002.8, 1003.6, 1003.5, 1004.5, 1005.3, 1005.5, 1006.3, 1006.9, 1006.9, 1007.7, 1007.5, 1007.2, 1007.0, 1006.4, 1007.6, 1008.1, 1008.2, 1007.9, 1008.3, 1008.7, 1008.8, 1008.8, 1009.0, 1009.3, 1009.2, 1008.9, 1008.9, 1009.1, 1009.1, 1009.2, 1009.4, 1009.6, 1009.9, 1009.9, 1009.3, 1008.7, 1008.1, 1007.7, 1007.5, 1007.6, 1007.8, 1007.8, 1007.5, 1007.3, 1007.2, 1007.1], 'visibility': [5080.0, 2640.0, 3780.0, 4460.0, 4560.0, 4180.0, 3280.0, 2740.0, 1220.0, 3020.0, 13880.0, 18320.0, 23000.0, 37300.0, 42920.0, 42540.0, 41080.0, 32700.0, 25280.0, 22620.0, 19800.0, 16520.0, 12740.0, 9220.0, 6620.0, 4920.0, 4000.0, 3320.0, 3240.0, 3320.0, 3980.0, 4220.0, 5200.0, 8440.0, 15960.0, 26640.0, 34880.0, 40240.0, 47400.0, 49820.0, 41380.0, 22360.0, 13860.0, 12140.0, 14580.0, 15980.0, 15200.0, 14700.0]} 
               dostajemy dane od północy danego dnia - więc to logiczne, że 18 następnego dnia to 24+18 wartość z tej tablicy 
                """
                
                tomorrow_data = {
                    'description': _get_weather_description(daily.get('weather_code', [0, 0])[1]),
                    'temperature': _round(_avg_values(hourly.get('temperature_2m', []), tomorrow_start, tomorrow_end)),
                    'apparent_temperature': _round(_avg_values(hourly.get('apparent_temperature', []), tomorrow_start, tomorrow_end)),
                    'dew_point': _round(_avg_values(hourly.get('dew_point_2m', []), tomorrow_start, tomorrow_end)),
                    'humidity': _round(_avg_values(hourly.get('relative_humidity_2m', []), tomorrow_start, tomorrow_end)),
                    'wind_speed': _round(_avg_values(hourly.get('wind_speed_10m', []), tomorrow_start, tomorrow_end)),
                    'pressure': _convert_pressure(_round(_avg_values(hourly.get('surface_pressure', []), tomorrow_start, tomorrow_end)), unit),
                    'visibility': _convert_visibility(_round(_avg_values(hourly.get('visibility', []), tomorrow_start, tomorrow_end)), unit),
                    'image_code': get_weather_image_code(daily.get('weather_code', [0, 0])[1])
                }
                weather_list.append(tomorrow_data)

        return weather_list if weather_list else None
        
    except Exception as e:
        print(f"Błąd podczas pobierania danych pogodowych: {e}")
        return None


def _round(value):
    if value is None:
        return '--'
    try:
        return round(value, 1)
    except:
        return '--'


def _avg_values(values, start, end):
    if not values or len(values) <= end:
        return None

    slice_of_values = values[start:end + 1]
    valid_values = [value for value in slice_of_values if value is not None]

    if not valid_values:
        return None

    return sum(valid_values) / len(valid_values)


def _convert_pressure(pressure, unit):
    if pressure == '--':
        return '--'
    
    if unit == 'imperial':
        # konwersja z hPa na inHg
        return round(pressure * 0.02953, 2)
    return pressure


def _convert_visibility(visibility, unit):
    if visibility == '--':
        return '--'
    
    # visibility z API jest w metrach, my chcemy km lub mile
    if unit == 'imperial':
        # konwersja z metrów na mile
        return round(visibility / 1609.34, 1)
    else:
        # konwersja z metrów na kilometry
        return round(visibility / 1000, 1)


def _get_weather_description(weather_code):
    try:
        weather_code = int(weather_code)
        if weather_code in WEATHER_CODES:
            return WEATHER_CODES[weather_code]['description']
        else:
            return 'Nieznane warunki pogodowe'
    except:
        return 'Nieznane warunki pogodowe'


def get_weather_image_code(weather_code):
    try:
        weather_code = int(weather_code)
        if weather_code in WEATHER_CODES:
            return WEATHER_CODES[weather_code]['image']
        else:
            return 0  # domyślny obrazek - słoneczko
    except:
        return 0


def getCoordinatesByName(name):
    try:
        url = format_url(geocoding_api_url, 'format=json', 'count=10', 'language=pl', f'name={name}')
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Błąd podczas pobierania współrzędnych: {e}")
        return None

def getNameByCoordinates(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&accept-language=pl"
        headers_osm = {
            'User-Agent': 'WeatherApp/1.0',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers_osm, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'address' in data:
            city = data['address'].get('city') or data['address'].get('town') or data['address'].get(
                'village') or 'Nieznana miejscowość'
            return [{
                'name': city,
                'country': data['address'].get('country', 'Nieznany kraj'),
                'latitude': float(lat),
                'longitude': float(lon)
            }]
        return [
            {
                'name': "Nieznana lokalizacja",
                'country': "Nieznany kraj",
                'latitude': float(lat),
                'longitude': float(lon)
            }
        ]
    except Exception as e:
        print(f"Błąd podczas pobierania nazw: {e}")
        return None