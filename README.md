# HomeAutomationRelais

This is a Flask API, which connects to a FRITZ!box to gather informations about connected smart home devices. For this i'm using the [python-fritzhome](https://github.com/hthiery/python-fritzhome) python package. 
The API can then be used in other projects, for example with [MagicMirror²](https://github.com/MichMich/MagicMirror/). 
It also provides a small Website you can access at home with your mobile phone for easy switching power outlets or changing the temperature.

One could run the Flask server on a RaspberryPi, where also other gadgets are connected to the GPIO pins. 
For this the API also provides access to connected relais, LEDs or other commands you want to execute. Herefore it uses the [GPIOZero](https://github.com/gpiozero/gpiozero) Library. 

Behind the scenes all functionalites are packed into threads, which is maybe not best practice with Flask, but it reduces the amount of calls to the different (sub-)libraries and the load on the Pi. Feel free to propose a smarter solution :)

### Implemented FRITZ! Devices
--------------
While the python-fritzhome package provides many more devices, i'm focussing here on the following devices since i do not have more devices yet. 
Feel free to contribute error / display / api functions for missing devices

* [FRITZ!DECT 200](https://avm.de/produkte/fritzdect/fritzdect-200/)
* [Comet DECT](https://www.eurotronic.org/produkte/comet-dect.html)

### Example
--------------
![Example Screenshot](static/sample.png?raw=true "Example screenshot")

### Installation
--------------
Use a virtual environment to install all requirements

```python
python3 -m pip install -r requirements.txt
```

copy the config template to `config.json` and update it to your needs. This is a minimal configuration:

```python
{
    "main" : {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": true
    },

    "api": {
        "endpoint": "http://127.0.0.1:5000"
    },

    "fritz": {
        "enabled": false,
        "host": "", 
        "user": "",
        "password": ""
    },

    "pi": {
        "enabled": false
    }
}
```

You can then start the Flask Server by running 
```python
python3 webapp.py
```

After this you should be able to connect to the server by open a web browser and browse to `http://localhost:5000`. See the configuration options section for more options.

### Configuration Options
--------------

| Option                  | Details                                                                                           |
|-------------------------|---------------------------------------------------------------------------------------------------|
| `main:host`             | **Required** - Host where the Flask app should listen. 0.0.0.0 allows connections from everywhere |
| `main:port`             | **Required** - Port to listen |
| `main:debug` | run in debug mode |
|-------------------------|---------------------------------------------------------------------------------------------------|
| `api:endpoint` | endpoint for the API. Keep on 127.0.0.1:5000 if it runs only locally. If you want to access it from your local network, choose the ip of the device |
|-------------------------|---------------------------------------------------------------------------------------------------|
| `fritz:enabled` | boolean expression to enable this module. if set to `false` you can skip the other values in this section |
| `fritz:host` | Host of the fritzbox. |
| `fritz:user` | Username of the fritzbox user. see python-fritzhome documentation how to add a new user on the fritzbox |
| `fritz:password` | Password of the fritzbox user |
|-------------------------|---------------------------------------------------------------------------------------------------|
| `pi:enabled` | boolean expression to enable the Pi GPIOZero module. if set to `false` you can skip the other values in this section |
|-------------------------|---------------------------------------------------------------------------------------------------|

