from flask import Blueprint, jsonify, request
from module.mysqlmethods import mysql
from math import ceil
from module.cache import cache
from module.motcapi import motcAPI
import time

estimatetimeApi = Blueprint("estimatetimeApi", __name__)


@estimatetimeApi.route("/estimatetime", methods=["GET"])
def get_estimatetime_data():
    t1 = time.time()
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    stopBusTime = get_stop_estimate_time()
    t2 = time.time()
    returnData = dict()
    returnData["data"] = []
    # 找出所有該車站的站牌資料
    selectSql = f"SELECT stopUID FROM stopofstation WHERE stationUID = (SELECT stationUID FROM stationinfo WHERE coordinate = POINT({latitude}, {longitude}))"
    resultstopUID = mysql.readData(selectSql)
    # 找出站牌資料所屬路線UID
    allrouteUID = []
    returnData["data"].append({"routedata": {}})
    # 設定站牌狀態dictionary資料
    stopstatusmap = {1: "未發車", 2: "交管不停靠", 3: "末班車已過", 4: "今日未營運"}
    for eachstopUID in resultstopUID:
        # 於交通部資料中，偶爾會發生路線預計抵達車站時間缺漏，跳過該路線資料讀取
        if eachstopUID[0] not in stopBusTime:
            print(eachstopUID[0])
            continue
        else:
            # 把routeUID放進returnData["data"][0]["routedata"] 當KEY
            allrouteUID.append(stopBusTime[eachstopUID[0]]["RouteUID"])
            estimateTime = stopBusTime[eachstopUID[0]]["EstimateTime"]
            # estimatetime不為-1，表示有正確倒數秒數，取無條件進位分鐘數；取站牌狀態
            if estimateTime != -1:
                estimateStatus = (
                    "進站中" if estimateTime <= 60 else str(ceil(estimateTime / 60)) + "分"
                )
            else:
                estimateStatus = stopstatusmap.get(
                    stopBusTime[eachstopUID[0]]["StopStatus"]
                )
        returnData["data"][0]["routedata"][stopBusTime[eachstopUID[0]]["RouteUID"]] = {
            "direction": stopBusTime[eachstopUID[0]]["Direction"],
            "estimateStatus": estimateStatus,
        }
    routeUID_strings = "','".join(allrouteUID)
    selectSql = f"SELECT a.stopname_tw, a.stopname_en, b.routeUID, b.routename_tw, b.routename_en, b.depname_tw, b.depname_en, b.destname_tw, b.destname_en FROM stationinfo AS a, busroute AS b WHERE a.coordinate = POINT({latitude}, {longitude}) AND b.routeUID IN ('{routeUID_strings}')"
    resultrouteData = mysql.readData(selectSql)
    # 將站牌名中文英文新增至returnData
    stopname = {
        "stopname": {
            "tw": resultrouteData[0][0],
            "en": resultrouteData[0][1],
        }
    }
    returnData["data"].append(stopname)
    # 取得路線資訊新增至routeUID當KEY的returnData["data"][0]["routedata"]
    for routeData in resultrouteData:
        # 取得returnData中該routeUID現有資料，routeData[2] = routeUID
        dataNow = returnData["data"][0]["routedata"][routeData[2]]
        # 該路線起訖點中英文名
        depname_tw, depname_en, destname_tw, destname_en = (
            (routeData[7], routeData[8], routeData[5], routeData[6])
            if dataNow["direction"] == 1
            else (routeData[5], routeData[6], routeData[7], routeData[8])
        )
        returnData["data"][0]["routedata"][routeData[2]]["depdestname"] = {
            "depname_tw": depname_tw,
            "depname_en": depname_en,
            "destname_tw": destname_tw,
            "destname_en": destname_en,
        }
        # 該路線中英文名
        returnData["data"][0]["routedata"][routeData[2]]["routename"] = {
            "tw": routeData[3],
            "en": routeData[4],
        }
    t3 = time.time()
    print(f"estimatetimeAPI time: {t2-t1}")
    print(f"estimatetimeAPIClean time: {t3-t2}")
    return jsonify(returnData), 200


@cache.cached(timeout=15, key_prefix="stop_estimate_time")
def get_stop_estimate_time():
    from requests import request

    t4 = time.time()
    # Access data from MOTC ptx
    req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Taipei?$select=StopUID%2C%20RouteUID%2C%20Direction%2C%20EstimateTime%2C%20StopStatus&$format=JSON"
    response = request("get", req_url, headers=motcAPI.authHeader())
    response = response.json()
    stopBusTime = dict()
    try:
        for eachStop in response:
            # 尚未發車時部分站點未提供EstimateTime
            if "EstimateTime" not in eachStop:
                eachStop["EstimateTime"] = -1
            stopBusTime[eachStop["StopUID"]] = {
                "RouteUID": eachStop["RouteUID"],
                "Direction": eachStop["Direction"],
                "EstimateTime": eachStop["EstimateTime"],
                "StopStatus": eachStop["StopStatus"],
            }
    except Exception as error:
        with open("errorinAPI.txt", "a") as outfile:
            nowStruct = time.localtime(time.time())
            nowString = time.strftime("%a, %d %b %Y %H:%M:%S", nowStruct)
            errorStr = nowString + "\n" + str(error) + "\n"
            outfile.writelines(errorStr)
            outfile.writelines("ptx response:")
            outfile.writelines(response)
    t5 = time.time()
    print("estimatetimeAPI cache REAL", t5 - t4)
    return stopBusTime
