# Read environmental metrics from PiicoDev sensors
from enum import Enum
from typing import Dict, Any, Union
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from PiicoDev_ENS160 import PiicoDev_ENS160 # Air quality sensor
from PiicoDev_BME280 import PiicoDev_BME280 # Atmospheric sensor
from PiicoDev_VEML6030 import PiicoDev_VEML6030 # Light sensor
from PiicoDev_Unified import sleep_ms       # a cross-platform sleep function

class EnvironmentSensor:
    class Mode(Enum):
        TEST = "Test"
        PROD = "Prod"

    def __init__(self, mode=Mode.TEST) -> None:
        load_dotenv()
        self.PASSWORD = os.getenv("WEATHER_POST_PASSWORD")
        self.logfile = "LOG.txt"
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
            "air_quality_index": aqi[0],
            "TVOC": tvoc,
            "eCO2": eco2[0],
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
        data = self.get_all_sensor_values()
        # Also add in password to data
        data["password"] = self.PASSWORD
        print(f'data is {data}')
        # Post to my api endpoint to add to database
        self.make_post_request("https://api.ashwingur.com/weather", data)

    def make_post_request(self, url, data, max_attempts=3):
        """
        Make a POST request to the specified URL with the provided data.
        
        Parameters:
            url (str): The URL endpoint to send the POST request to.
            data (dict): The data to be sent in the POST request.
            max_attempts (int): The maximum number of attempts to make the request (default: 3).
        
        Returns:
            requests.Response: The response object if the request was successful, else None.
        """
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(url, json=data)
                if response.status_code == 201:
                    print("POST request was successful!")
                    self.log_message(f"POST success, data: {data}", self.logfile)
                    return response
                else:
                    print(f"Attempt {attempt}: POST request failed with status code: {response.status_code}. Response: {response.text}")
                    self.log_message(f"Attempt {attempt}: POST request failed with status code: {response.status_code}", self.logfile)
            except requests.RequestException as e:
                print(f"Attempt {attempt}: An error occurred: {e}")
                self.log_message(f"Attempt {attempt}: An error occurred: {e}", self.logfile)
            
            # If this is not the last attempt, wait for a moment before retrying
            if attempt < max_attempts:
                print("Retrying in 1 second...")
                sleep_ms(3000)
        
        print(f"Reached maximum number of attempts ({max_attempts}). Giving up.")
        return None

    def log_message(self, message, log_file):
        """
        Log a message to a text file with a timestamp.

        Parameters:
            message (str): The message to log.
            log_file (str): The path to the log file.

        Returns:
            None
        """
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create the log message with timestamp
        log_entry = f"[{timestamp}] {message}\n"

        # Write the log message to the file
        with open(log_file, "a") as file:
            file.write(log_entry)


if __name__ == '__main__':
    sensor = EnvironmentSensor(mode=EnvironmentSensor.Mode.PROD)
    sensor.run()