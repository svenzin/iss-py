# ISS-py, a reminder of International Space Station passes for RaspberryPi

ISS-py is a small program that will help you remember when the ISS will be visible in your sky.
It uses the Sense Hat's matrix display to tell you when is the next pass will happen.
It will also track the station while it's crossing the sky in case you're stuck under the clouds.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* RaspberryPi
* Sense Hat

### Step-by-step installation from a fresh Raspbian

Enable I2C

    sudo raspi-config

Update the system

    apt update
    sudo apt upgrade

Install dependencies

    sudo apt install git python3-lxml python3-cssselect sense-hat

Get the code

    git clone https://github.com/svenzin/iss-py.git

Create configuration file
Run the following command and follow the instructions.
It will generate a config.json file with the required information.

    python3 iss-py/config.py

Run ISS-py

    python3 iss-py/iss-py.py -f config.json

### Run on startup

Add the following line to your cron

    @reboot python3 /home/pi/iss-py/iss-py.py -f /home/pi/config.json > /home/pi/iss-py.log
