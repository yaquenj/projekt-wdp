import json
from enum import StrEnum


def createDefaultConfig():
    default_config = {
        "location": {
          "name": "Rzeszów",
          "country": "Polska",
          "lat": 50.04132,
          "lon": 21.99901
        },
        "preferences": {
              "unit": "metric",
              "factors": [
                  1,
                  5,
                  3,
                  2,
                  4,
                  7
              ]
        }
    }
    saveConfig(default_config)
    return default_config


def readConfig():
    config_raw = open("./config.json")
    config = json.load(config_raw)
    config_raw.close()
    return config


def saveConfig(config):
    with open("./config.json", "w") as config_file:
        json.dump(config, config_file, indent=2)
        config_file.close()


def setLocation(name, country, lat, lon):
    config = readConfig()
    config["location"] = {
        "name": name,
        "country": country,
        "lat": lat,
        "lon": lon
    }
    saveConfig(config)


def setFactors(factors):
    config = readConfig()
    config["preferences"]["factors"] = factors
    saveConfig(config)


def addFactor(factor):  # od 2 do 6 max
    config = readConfig()
    config["preferences"]["factors"].append(factor)
    saveConfig(config)


def removeFactor(factor):
    config = readConfig()
    factors = config["preferences"]["factors"]
    if factor in factors:
        factors.remove(factor)
        saveConfig(config)

class Units(StrEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"


def setUnit(unit=Units):
    config = readConfig()
    config["preferences"]["unit"] = unit
    saveConfig(config)
