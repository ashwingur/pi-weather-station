# Read environmental metrics from PiicoDev sensors
from enum import Enum
from typing import Dict, Any, Union

from PiicoDev_ENS160 import PiicoDev_ENS160 # Air quality sensor
from PiicoDev_BME280 import PiicoDev_BME280 # Atmospheric sensor
from PiicoDev_VEML6030 import PiicoDev_VEML6030 # Light sensor
from PiicoDev_Unified import sleep_ms       # a cross-platform sleep function

class EnvironmentSensor:
    class Mode(Enum):
        TEST = "Test"
        PROD = "Prod"

    def __init__(self, mode=Mode.TEST) -> None:
        self.mode = mode
        self.air_quality_sensor = PiicoDev_ENS160()   # Initialise the ENS160 module
        self.atmospheric_sensor = PiicoDev_BME280()
        self.light_sensor = PiicoDev_VEML6030()

    def run(self):
        if self.mode == EnvironmentSensor.Mode.TEST:
            self.test_mode()
        else:
            self.prod_mode()

    def get_all_sensor_values(self) -> Dict[str, Union[float, int]]:
        """
        Read data from all the sensors and return it in a Python dictionary.

        Returns:
            dict: A dictionary containing sensor values.
                - "pressure" (float): Atmospheric pressure in hPa (millibars).
                - "humidity" (float): Relative humidity in percentage.
                - "temperature" (float): Temperature in Celsius.
                - "air_quality_index" (int): Air quality index.
                - "TVOC" (int): Total Volatile Organic Compounds concentration in parts per billion (ppb).
                - "eCO2" (int): Equivalent Carbon Dioxide concentration in parts per million (ppm).
                - "ambient_light" (float): Ambient light intensity in lux.
        """
        # Read data from the air quality sensor
        aqi = self.air_quality_sensor.aqi
        tvoc = self.air_quality_sensor.tvoc
        eco2 = self.air_quality_sensor.eco2

        # Read data from the atmospheric sensor
        tempC, presPa, humRH = self.atmospheric_sensor.values()  # Read all data
        pres_hPa = presPa / 100  # Convert Pascals to hPa (millibars)

        # Read data from the light sensor
        light_val = self.light_sensor.read()

        # Construct and return a dictionary with sensor values
        return {
            "pressure": pres_hPa,
            "humidity": humRH,
            "temperature": tempC,
            "air_quality_index": aqi,
            "TVOC": tvoc,
            "eCO2": eco2,
            "ambient_light": light_val
        }

    def test_mode(self):
        while True:
            sensor_values = self.get_all_sensor_values()
            for key, val in sensor_values.items():
                print(f'{key}: {val}')
            print('--------------------------')
            sleep_ms(1000)

    def prod_mode(self):
        pass


if __name__ == '__main__':
    sensor = EnvironmentSensor(mode=EnvironmentSensor.Mode.TEST)
    sensor.run()