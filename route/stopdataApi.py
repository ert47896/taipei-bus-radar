from flask import Blueprint, jsonify, request
from module.mysqlmethods import mysql
from module.cache import cache
from module.distance_latlng import calDistance
import googlemaps, os
from dotenv import load_dotenv

load_dotenv()
# 300公尺轉換為經緯度約為0.003度
diffRange = 0.003
gmaps = googlemaps.Client(key=os.getenv("gecode_key"))
stoplocationApi = Blueprint("stoplocationApi", __name__)
stopsApi = Blueprint("stopsApi", __name__)


@stoplocationApi.route("/stoplocation", methods=["GET"])
@cache.cached(timeout=300, key_prefix="stop_location")
def get_stop_status():
    # 由資料庫取出所需資料
    selectSql = "SELECT stopname_tw, stopname_en, address, ST_Y(coordinate), ST_X(coordinate) FROM stationinfo"
    result = mysql.readData(selectSql)
    if "error" in result:
        return jsonify(result), 500
    returnData = dict()
    returnData["data"] = []
    for rowData in result:
        temp = {
            "stopname": {"tw": rowData[0], "en": rowData[1]},
            "address": rowData[2],
            "longitude": rowData[3],
            "latitude": rowData[4],
        }
        returnData["data"].append(temp)
    return jsonify(returnData), 200


@stopsApi.route("/stops", methods=["GET"])
def get_stops_data():
    method = request.args.get("method")
    locationData = request.args.get("keyword")
    returnData = dict()
    returnData["data"] = []
    if method == "latlng":
        splitTemp = locationData.split(",")
        lat = float(splitTemp[0])
        lng = float(splitTemp[1])
    elif method == "address":
        # 將地址轉換為經緯度資料
        geocodeResult = gmaps.geocode(locationData, language="zh-TW")
        # 判斷該地址有無回復資料
        if len(geocodeResult) == 0:
            return jsonify({"data": "該地址查無相符資料"}), 200
        lat = geocodeResult[0]["geometry"]["location"]["lat"]
        lng = geocodeResult[0]["geometry"]["location"]["lng"]
    else:
        return jsonify({"error": "請確認搜尋資訊"}), 400
    temp = {
        "method": method,
        "locationData": locationData,
        "selectLat": lat,
        "selectLng": lng,
    }
    # 由資料庫取出目標位置鄰近300公尺站牌資料
    selectSql = f"SELECT stopname_tw, address, ST_X(coordinate), ST_Y(coordinate) FROM stationinfo \
        WHERE ST_X(coordinate) BETWEEN {lat-diffRange} AND {lat+diffRange} AND ST_Y(coordinate) BETWEEN {lng-diffRange} AND {lng+diffRange}"
    result = mysql.readData(selectSql)
    if len(result) == 0:
        temp["stops"] = "無鄰近站牌資料"
    else:
        temp["stops"] = []
        for eachStop in result:
            distance = calDistance([lng, lat], [eachStop[3], eachStop[2]])
            if distance <= 0.3:
                stopData = {
                    "stopname_tw": eachStop[0],
                    "address": eachStop[1],
                    "latitude": eachStop[2],
                    "longitude": eachStop[3],
                    "distance": round(distance * 1000),
                }
                temp["stops"].append(stopData)
    returnData["data"].append(temp)
    return jsonify(returnData), 200