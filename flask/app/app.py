from flask import Flask, render_template
from module import cache
from route.buslocationApi import buslocationApi
from route.stopdataApi import stoplocationApi, stopsApi, stopApi
from route.estimatetimeApi import estimatetimeApi
from route.routedataApi import routesApi, routeApi, routestatusApi

app = Flask(__name__, static_folder="public", static_url_path="/")

app.config["JSON_AS_ASCII"] = False  # False避免中文顯示為ASCII編碼
app.config["TEMPLATES_AUTO_RELOAD"] = True  # True當flask偵測到template有修改會自動更新

cache.set_cache(app)


# Pages
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/routes")
def routes_page():
    return render_template("routes.html")


@app.route("/route/<routename>")
def each_route(routename):
    return render_template("route.html")


@app.route("/stops")
def stops_page():
    return render_template("stops.html")


@app.route("/stop/<stopname>/<float:latitude>/<float:longitude>")
def stop_page(stopname, latitude, longitude):
    return render_template("stop.html")


# API
app.register_blueprint(buslocationApi, url_prefix="/api")
app.register_blueprint(stoplocationApi, url_prefix="/api")
app.register_blueprint(stopsApi, url_prefix="/api")
app.register_blueprint(stopApi, url_prefix="/api")
app.register_blueprint(estimatetimeApi, url_prefix="/api")
app.register_blueprint(routesApi, url_prefix="/api")
app.register_blueprint(routeApi, url_prefix="/api")
app.register_blueprint(routestatusApi, url_prefix="/api")

if __name__ == "__main__":
    app.run(host ='0.0.0.0')
