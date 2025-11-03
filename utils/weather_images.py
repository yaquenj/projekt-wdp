from enum import Enum

class ImageCode(Enum):
    SUN = 0
    SUN_CLOUD = 1
    CLOUD = 2
    FOG = 3
    DRIZZLE = 4
    FREEZING_DRIZZLE = 5
    LIGHT_RAIN = 6
    RAIN = 7
    FREEZING_RAIN = 8
    SNOW = 9
    HAIL = 10
    STORM = 11
    THUNDERSTORM = 12

    ERROR = 404

    HOT = 100
    COLD = 101
    HUMIDITY = 102
    WIND = 103
    DEW_POINT = 104
    VISIBILITY = 105
    PRESSURE = 106

def get_image_name(en):
    match en:
        case ImageCode.SUN:
            return "sun.png"
        case ImageCode.SUN_CLOUD:
            return "sun-behind-a-cloud.png"
        case ImageCode.CLOUD:
            return "cloud.png"
        case ImageCode.FOG:
            return "fog.png"
        case ImageCode.DRIZZLE:
            return "drizzle.png"
        case ImageCode.LIGHT_RAIN:
            return "light_rain.png"
        case ImageCode.RAIN:
            return "heavy-rain.png"
        case ImageCode.FREEZING_RAIN:
            return "freezing_rain.png"
        case ImageCode.FREEZING_DRIZZLE:
            return "freezing_drizzle.png"
        case ImageCode.SNOW:
            return "snow.png"
        case ImageCode.HAIL:
            return "hail.png"
        case ImageCode.STORM:
            return "storm.png"
        case ImageCode.THUNDERSTORM:
            return "thunderstorm.png"
        case ImageCode.ERROR:
            return "error.png"
        case ImageCode.HOT:
            return "hot.png"
        case ImageCode.COLD:
            return "cold.png"
        case ImageCode.HUMIDITY:
            return "humidity.png"
        case ImageCode.WIND:
            return "wind.png"
        case ImageCode.PRESSURE:
            return "pressure.png"
        case ImageCode.DEW_POINT:
            return "leaf.png"
        case ImageCode.VISIBILITY:
            return "length.png"
        case _:
            return "question.png"
