from flask import Blueprint, jsonify
from module.mysqlmethods import mysql
from module.cache import cache
import gc

stoplocationApi = Blueprint("stoplocationApi", __name__)


@stoplocationApi.route("/stoplocation", methods=["GET"])
@cache.cached(timeout=300, key_prefix="stop_location")
def getStopstatus():
    # gc.collect()
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
