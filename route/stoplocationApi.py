from flask import Blueprint, jsonify
from module.mysqlmethods import Sqlmethod

stoplocationApi = Blueprint("stoplocationApi", __name__)

# 操作mysql CRUD; cudData(query, value) return {"ok":True}成功;
# readData(query, value=None) return 查詢資料 {"error"}錯誤
mysql = Sqlmethod()

@stoplocationApi.route("/stoplocation", methods=["GET"])
def getStopstatus():
    # 由資料庫取出所需資料
    selectSql = "SELECT stopname_tw, stopname_en, address, ST_Y(coordinate), ST_X(coordinate) FROM stationinfo"
    result = mysql.readData(selectSql)
    if "error" in result:
        return jsonify(result), 500
    returnData = dict()
    returnData["data"] = []
    for rowData in result:
        temp = {
            "stopname": {
                "tw": rowData[0],
                "en": rowData[1]
            },
            "address": rowData[2],
            "longitude": rowData[3],
            "latitude": rowData[4]
        }
        returnData["data"].append(temp)
    return jsonify(returnData), 200