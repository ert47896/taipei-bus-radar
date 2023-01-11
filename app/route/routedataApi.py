from flask import Blueprint, jsonify, request
from module.mysqlmethods import mysql
from module.tdxapi import get_data
from module.cache import cache
from shapely.wkt import loads
from .estimatetimeApi import get_stop_estimate_time
from .buslocationApi import get_route_bus_location
from math import ceil
import time

routesApi = Blueprint("routesApi", __name__)
routeApi = Blueprint("routeApi", __name__)
routestatusApi = Blueprint("routeStatusApi", __name__)


@routesApi.route("/routes", methods=["GET"])
def get_routedata():
    # Access data from mysql
    keyword = request.args.get("keyword")
    selectSql = "SELECT routename_tw FROM busroute WHERE routename_tw LIKE %s ORDER BY routename_tw"
    selectValue = ("%" + keyword + "%",)
    result = mysql.readData(selectSql, selectValue)
    returnData = dict()
    # 查無路線資料
    if len(result) == 0:
        returnData["data"] = "查無路線資料"
    else:
        returnData["data"] = {
            "觀光巴士": [],
            "捷運紅線接駁公車": [],
            "捷運藍線接駁公車": [],
            "捷運綠線接駁公車": [],
            "捷運棕線接駁公車": [],
            "幹線公車": [],
            "通勤公車": [],
            "市民小巴": [],
            "小": [],
            "一般公車": [],
        }
        # 將路線分類方便前端頁面設計
        for index in range(len(result)):
            if "臺北觀光" in result[index][0]:
                returnData["data"]["觀光巴士"].append(result[index][0])
            elif "紅" in result[index][0]:
                returnData["data"]["捷運紅線接駁公車"].append(result[index][0])
            elif "藍" in result[index][0]:
                returnData["data"]["捷運藍線接駁公車"].append(result[index][0])
            elif "綠" in result[index][0]:
                returnData["data"]["捷運綠線接駁公車"].append(result[index][0])
            elif "棕" in result[index][0]:
                returnData["data"]["捷運棕線接駁公車"].append(result[index][0])
            elif "幹線" in result[index][0]:
                returnData["data"]["幹線公車"].append(result[index][0])
            elif "通勤" in result[index][0]:
                returnData["data"]["通勤公車"].append(result[index][0])
            elif "市民小巴" in result[index][0]:
                returnData["data"]["市民小巴"].append(result[index][0])
            elif "小" in result[index][0]:
                returnData["data"]["小"].append(result[index][0])
            else:
                returnData["data"]["一般公車"].append(result[index][0])
    return jsonify(returnData), 200


@routeApi.route("/route/<routename>", methods=["GET"])
def get_each_routedata(routename):
    # Access data from mysql
    selectSql = "SELECT b.routename_tw, ST_AsText(b.linestrings), b.depname_tw, b.destname_tw, b.routeimgurl, c.oname_tw, c.webpage FROM operatorofroute AS a JOIN busroute AS b ON a.routeUID = b.routeUID JOIN operator AS c ON a.operatorID = c.operatorID WHERE b.routename_tw = %s"
    selectValue = (routename,)
    result = mysql.readData(selectSql, selectValue)
    returnData = dict()
    returnData["data"] = dict()
    # 資料放入回傳字典除營運者資料(c.oname_tw, c.webpage)，因為一條路線可能多個業者經營，所以另外處理
    # LingString轉換為數值以經緯度分成兩個陣列[0]經度 [1]緯度
    line = result[0][1]
    # 判斷有無路線線型資料
    if line == None:
        lineLatLon = "未提供路線資料"
    else:
        lineData = loads(line).xy
        lineLatLon = []
        for index in range(len(lineData[0])):
            lineLatLon.append([lineData[1][index], lineData[0][index]])
    returnData["data"] = {
        "routename_tw": result[0][0],
        "lineLatLon": lineLatLon,
        "depname_tw": result[0][2],
        "destname_tw": result[0][3],
        "routeimgurl": result[0][4],
    }
    returnData["data"]["operator"] = []
    for eachOperator in result:
        returnData["data"]["operator"].append(
            {"oname_tw": eachOperator[5], "webpage": eachOperator[6]}
        )
    return jsonify(returnData), 200


@routestatusApi.route("/routestatus/<routename>", methods=["GET"])
def get_routestatus(routename):
    selectSql = "SELECT a.stopUID, d.routeUID, b.stopname_tw, b.address, ST_Y(b.coordinate), ST_X(b.coordinate), c.direction FROM stopofstation AS a JOIN stationinfo AS b ON a.stationUID = b.stationUID JOIN stopofroute AS c ON a.stopUID = c.stopUID JOIN busroute AS d ON c.routeUID = d.routeUID WHERE d.routename_tw = %s"
    selectValue = (routename,)
    result = mysql.readData(selectSql, selectValue)
    returnData = dict()
    # key=0 去程資料，key=1 返程資料
    returnData["data"] = {
        0: {"OperateBus": [], "StopsData": []},
        1: {"OperateBus": [], "StopsData": []},
    }
    # 此路線routeUID
    routeUID = result[0][1]
    # 取得該路線公車行駛資料(key routeUID)，資料型態list
    # 檢查路線上有公車營運才整理"OperateBus"資料
    responsebuslocation = get_route_bus_location()["data"]
    if routeUID in responsebuslocation:
        buslocation = get_route_bus_location()["data"][routeUID]["OperateBus"]
        for eachBus in buslocation:
            busdata = {
                "platenumb": eachBus["platenumb"],
                "latitude": eachBus["latitude"],
                "longitude": eachBus["longitude"],
                "speed": eachBus["speed"],
            }
            if eachBus["direction"] == 0:
                returnData["data"][0]["OperateBus"].append(busdata)
            else:
                returnData["data"][1]["OperateBus"].append(busdata)
    # 取得各站牌公車預計抵達時間(key stopUID)，資料型態dictionary
    stationstatus = get_stop_estimate_time()
    for eachStop in result:
        # 此站牌stopUID
        stopUID = eachStop[0]
        # 於交通部資料中，部分車站未提供預計抵達時間相關資料
        if stopUID not in stationstatus:
            estimatestatus = "無路線資料"
        else:
            estimateTime = stationstatus[stopUID]["EstimateTime"]
            # estimatetime不為-1，表示有正確倒數秒數；否則取站牌狀態
            # 設定站牌狀態dictionary資料
            stopstatusmap = {1: "未發車", 2: "交管不停靠", 3: "末班車已過", 4: "今日未營運"}
            if estimateTime != -1:
                estimatestatus = (
                    "進站中" if estimateTime < 120 else str(ceil(estimateTime / 60)) + "分"
                )
            else:
                estimatestatus = stopstatusmap.get(stationstatus[stopUID]["StopStatus"])
        stopdata = {
            "stopUID": eachStop[0],
            "stopname": eachStop[2],
            "latitude": eachStop[4],
            "longitude": eachStop[5],
            "address": eachStop[3],
            "estimatestatus": estimatestatus,
            "platenumb": [],
        }
        if eachStop[6] == 0:
            returnData["data"][0]["StopsData"].append(stopdata)
        else:
            returnData["data"][1]["StopsData"].append(stopdata)
    # 取得公車目前所在站牌序列(key routeUID)，資料型態list
    # 檢查路線上有公車營運才整理"公車位處哪個站牌"資料，用站牌UID判斷，以站序判斷的話會有誤差(有些路線部分站點
    # 不一定每班都停靠)；以站名判斷的話也會有誤差(部分路線有重複站名)
    responsedata = get_bus_on_stop()["data"]
    if routeUID in responsedata:
        busonstop = responsedata[routeUID]
        for eachbusonstop in busonstop:
            # 該公車所處站牌UID
            busonStopUID = eachbusonstop["stopUID"]
            if eachbusonstop["direction"] == 0:
                for eachstop in returnData["data"][0]["StopsData"]:
                    if eachstop["stopUID"] == busonStopUID:
                        eachstop["platenumb"].append(eachbusonstop["platenumb"])
            else:
                for eachstop in returnData["data"][1]["StopsData"]:
                    if eachstop["stopUID"] == busonStopUID:
                        eachstop["platenumb"].append(eachbusonstop["platenumb"])
    return jsonify(returnData), 200


@cache.cached(timeout=15, key_prefix="bus_on_stops")
def get_bus_on_stop():
    from requests import request

    # Access data from MOTC ptx (transfer from PTX to TDX)
    # req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeNearStop/City/Taipei?$select=PlateNumb%2C%20DutyStatus%2C%20RouteUID%2C%20Direction%2C%20StopUID&$filter=DutyStatus%20eq%201%20or%20DutyStatus%20eq%200&$format=JSON"
    # Access data from MOTC TDX
    req_url = "https://tdx.transportdata.tw/api/basic/v2/Bus/RealTimeNearStop/City/Taipei?$select=PlateNumb%2C%20DutyStatus%2C%20RouteUID%2C%20Direction%2C%20StopUID&$filter=DutyStatus%20eq%201%20or%20DutyStatus%20eq%200&$format=JSON"
    response = get_data(req_url)
    response = response.json()
    returnData = dict()
    returnData["data"] = dict()
    try:
        for stopBusData in response:
            # 檢查routeUID有沒有在returnData["data"]當key
            if stopBusData["RouteUID"] not in returnData["data"]:
                returnData["data"][stopBusData["RouteUID"]] = []
            returnData["data"][stopBusData["RouteUID"]].append(
                {
                    "platenumb": stopBusData["PlateNumb"],
                    "direction": stopBusData["Direction"],
                    "stopUID": stopBusData["StopUID"],
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
    return returnData
