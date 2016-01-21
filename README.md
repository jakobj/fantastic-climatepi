# fantastic-climatepi

to keep an eye on temperature and humidity using the raspberry pi.

* uses the [pigpio](http://abyz.co.uk/rpi/pigpio/) library to read out temperature and humidity from an DHT22 sensor
* stores the data in a [sqlite](https://www.sqlite.org/) database
* serves a webpage with information about the current status and a visualization of past data via a [tornado](http://www.tornadoweb.org/en/stable/) webservice

tutorials:
 * https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/overview
 * http://www.jasm.eu/2013/05/28/raspberry-pi-temperature-and-humidity-sensor/
 * https://www.youtube.com/watch?v=IHTnU1T8ETk
