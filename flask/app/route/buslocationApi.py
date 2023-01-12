from flask import Blueprint, jsonify
from module.mysqlmethods import mysql
from module.tdxapi import get_data
from module.cache import cache
import time

buslocationApi = Blueprint("buslocationApi", __name__)


@buslocationApi.route("/buslocation", methods=["GET"])
def get_bus_location():
    # 取得所有路線公車位置資料
    returnData = get_route_bus_location()
    return jsonify(returnData), 200


@cache.cached(timeout=15, key_prefix="bus_location")
def get_route_bus_location():
    # Access data from MOTC ptx (transfer from PTX to TDX)
    # req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeByFrequency/City/Taipei?$select=PlateNumb%2C%20RouteUID%2C%20BusPosition%2C%20Speed%2C%20Direction&$filter=DutyStatus%20eq%201%20or%20DutyStatus%20eq%200&$format=JSON"
    # Access data from MOTC TDX
    req_url = "https://tdx.transportdata.tw/api/basic/v2/Bus/RealTimeByFrequency/City/Taipei?$select=PlateNumb%2C%20RouteUID%2C%20BusPosition%2C%20Speed%2C%20Direction&$filter=DutyStatus%20eq%201%20or%20DutyStatus%20eq%200&$format=JSON"
    # response = request("get", req_url, headers=motcAPI.authHeader())
    response = get_data(req_url)
    response = response.json()
    busRouteUID = []
    returnData = dict()
    returnData["data"] = dict()
    try:
        for eachBusData in response:
            if eachBusData["RouteUID"] not in busRouteUID:
                busRouteUID.append(eachBusData["RouteUID"])
                returnData["data"][eachBusData["RouteUID"]] = dict()
                returnData["data"][eachBusData["RouteUID"]]["OperateBus"] = []
            returnData["data"][eachBusData["RouteUID"]]["OperateBus"].append(
                {
                    "platenumb": eachBusData["PlateNumb"],
                    "direction": eachBusData["Direction"],
                    "longitude": eachBusData["BusPosition"]["PositionLon"],
                    "latitude": eachBusData["BusPosition"]["PositionLat"],
                    "speed": eachBusData["Speed"],
                }
            )
    except Exception as error:
        with open("errorinAPI.txt", "a") as outfile:
            nowStruct = time.localtime(time.time())
            nowString = time.strftime("%a, %d %b %Y %H:%M:%S", nowStruct)
            errorStr = nowString + "\n" + str(error) + "\n"
            outfile.writelines(errorStr)
            outfile.writelines("ptx response:")
            outfile.writelines(response)
    routeUID_strings = "','".join(busRouteUID)
    selectSql = f"SELECT routeUID, routename_tw, routename_en, depname_tw, depname_en, destname_tw, destname_en FROM busroute WHERE routeUID IN ('{routeUID_strings}')"
    result = mysql.readData(selectSql)
    for routeData in result:
        returnData["data"][routeData[0]]["routename"] = {
            "tw": routeData[1],
            "en": routeData[2],
        }
        returnData["data"][routeData[0]]["depdestname"] = {
            "depname_tw": routeData[3],
            "depname_en": routeData[4],
            "destname_tw": routeData[5],
            "destname_en": routeData[6],
        }
    return returnData
