from enum import Enum

class Factors(Enum):
    TEMPERATURE = 1
    WIND = 2
    HUMIDITY = 3
    PRESSURE = 4
    DEW_POINT = 5
    APPARENT_TEMPERATURE = 6
    VISIBILITY = 7

def get_factor_name(en):
    match en:
        case Factors.TEMPERATURE:
            return "temperature_2m"
        case Factors.WIND:
            return "wind_speed_10m"
        case Factors.HUMIDITY:
            return "relative_humidity_2m"
        case Factors.PRESSURE:
            return "surface_pressure"
        case Factors.DEW_POINT:
            return "dew_point_2m"
        case Factors.APPARENT_TEMPERATURE:
            return "apparent_temperature"
        case Factors.VISIBILITY:
            return "visibility"
        case _:
            print("Factor not found! Returning Temperature...")
            return "temperature_2m"
