# Główne funkcje aplikacji
from .spawnWindow import spawnWindow

# Funkcje API
from .api_calls import (
    getWeather,
    getCoordinatesByName,
    getNameByCoordinates,
    get_weather_image_code
)

# Funkcje zarządzania konfiguracją
from .config_manager import (
    readConfig,
    saveConfig,
    setLocation,
    setFactors,
    addFactor,
    removeFactor,
    setUnit,
    Units
)

# Funkcje pomocnicze
from .format_url import format_url

# Enumy - Obrazki pogodowe
from .weather_images import (
    get_image_name,
    ImageCode
)

# Enumy - Czynniki pogodowe
from .factors import (
    get_factor_name,
    Factors
)

# Publiczne API modułu
__all__ = [
    # Główne funkcje
    'spawnWindow',

    # API
    'getWeather',
    'getCoordinatesByName',
    'getNameByCoordinates',
    'get_weather_image_code',

    # Konfiguracja
    'readConfig',
    'saveConfig',
    'setLocation',
    'setFactors',
    'addFactor',
    'removeFactor',
    'setUnit',
    'Units',

    # Pomocnicze
    'format_url',

    # Obrazki
    'get_image_name',
    'ImageCode',

    # Czynniki
    'get_factor_name',
    'Factors'
]