# coding utf-8
from flask import Flask
from flask import request, jsonify, make_response
from flask import render_template
from flask_cors import cross_origin, CORS

from core.utils.Log import log

import json
import os

def init_webapp(cfg):
    app = Flask(__name__)

    # init fritz home connection if available
    if cfg["fritz"]["enabled"]:
        try:
            from core.Fritz import FritzHome
            fh = FritzHome(cfg["fritz"]["host"], cfg["fritz"]["user"], cfg["fritz"]["password"])
        except Exception as e:
            log.error("failed to init FritzHome Connection, is it installed?")
            log.error(str(e))
            fh = None
    else:
        fh = None
    app.config["fritz"] = fh

    # if requested, try to enable Pi related stuff
    if cfg["pi"]["enabled"]:
        try:
            from core.Pi import PiDevices
            pi = PiDevices()
        except Exception as e:
            log.error("failed to init pi devices. is gpiozero installed?")
            log.error(str(e))
            pi = None

        # add devices
        if pi:
            for gadget_def in cfg["pi"]["gadgets"]:
                pi.add_gadget(gadget_def)
            
    else: 
        pi = None
    app.config["pi"] = pi

    app.config["config"] = cfg

    with app.app_context():
        if app.config["fritz"]:
            app.config["fritz"].start()
        if app.config["pi"]:
            app.config["pi"].start()
        return app

config = "config.json"
if not os.path.exists(config):
    log.error("failed to load config file {}".format(config))
    sys.exit(1)

with open(config, "r") as configfile:
    cfg = json.load(configfile)
    log.debug("read config from {}".format(config))

app = init_webapp(cfg)  
CORS(app)

@app.route("/")
def entry_point():
    return render_template("index.html", \
            fh=app.config["fritz"], 
            pi=app.config["pi"], 
            config=app.config["config"])

@app.route("/toggle", methods=["POST"])
@cross_origin()
def toggle_switch():
    body = request.json
    if not "name" in body:
        return jsonify("no name provided"), 404

    fh = app.config["fritz"]
    if fh is None:
        return jsonify("Fritz not available / enabled"), 404
    name = body["name"]
    dev = fh.get_device(name)
    if not dev:
        return jsonify("device not found"), 404

    if not dev["has_switch"]:
        return jsonify("device has no switch capability"), 500

    new_state = not dev["state"]
    fh.set_switch(name, new_state)

    return jsonify(new_state), 200

@app.route("/pi_pressed", methods=["POST"])
@cross_origin()
def pi_pressed():
    pi = app.config["pi"]
    if pi is None:
        return jsonify("Pi not available / enabled"), 404
    body = request.json
    if not "name" in body:
        return jsonify("name not set"), 404

    gadget = pi.get_gadget(body["name"])
    if not gadget:
        return jsonify("unknown gadget with name '{}'".format(name))
    
    res = pi.do_action(body["name"])
    return jsonify(res), 200

@app.route("/temp", methods=["POST"])
@cross_origin()
def set_temp():
    body = request.json
    if not "name" in body or not "temp" in body:
        return jsonify("name and temp not set"), 404

    temp = body["temp"]
    fh = app.config["fritz"]
    if fh is None:
        return jsonify("Fritz not available / enabled"), 404

    name = body["name"]
    if name == "all":
        names = fh.get_devices()
    else:
        names = [name]

    if (temp == "away"):
        if cfg["fritz"]["away"] == "disabled":
            log.error("requesting away mode, but its disabled in the config file, aborting")
            return jsonify("away mode disabled"), 500
        fh.toggle_away_mode(cfg["fritz"]["away"])
        return jsonify("enabled away mode"), 200

    for name in names:
        dev = fh.get_device(name)

        if not dev:
            continue
        if dev["status"] != "ok":
            continue
        if not dev["has_thermostat"]:
            continue

        req = body["temp"]
        if type(req) == str:
            if req == "off":
                temp = 0
            elif req == "on":
                temp = 100
            elif req == "eco":
                temp = dev["eco"]
            elif req == "comfort":
                temp = dev["comfort"]
            else:
                return jsonify("unknown temperature identifier"), 500

        log.debug("set temp {} on device {}".format(body["temp"], name))
        fh.set_temp(name, temp)

    return jsonify(temp), 200

@app.route("/get", methods=["GET"])
@cross_origin()
def get_fritz():
    ain = request.args.get("ain")
    name = request.args.get("name")
    fh = app.config["fritz"]
    if fh is None:
        return jsonify("Fritz not available / enabled"), 404
    if not (ain or name):
        return jsonify({"devices": fh.get_devices()}), 200
    
    if ain:
        name = fh.get_name_by_ain(ain)
        if not name:
            return jsonify("unknown ain '{}'".format(ain)), 404

    dev = fh.get_device(name)
    if not dev:
        return jsonify("device not found"), 404

    return jsonify(dev), 200

@app.route("/pi_get", methods=["GET"])
@cross_origin()
def get_pi():
    name = request.args.get("name")
    pi = app.config["pi"]
    if pi is None:
        return jsonify("Pi not available / enabled"), 404
    if name is None:
        return jsonify({"gadgets": pi.get_gadgets()}), 200
    gadget = pi.get_gadget(name)
    if not gadget:
        return jsonify("gadget not found"), 404
    return jsonify(gadget), 200

if __name__ == "__main__":
    app.run(debug=cfg["main"]["debug"], host=cfg["main"]["host"], port=cfg["main"]["port"], use_reloader=False)#, ssl_context="adhoc")
