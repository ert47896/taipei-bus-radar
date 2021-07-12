from flask import Blueprint, jsonify, request
from module.mysqlmethods import Sqlmethod
from math import ceil
from module.cache import cache
from module.motcapi import Auth
import time

estimatetimeApi = Blueprint("estimatetimeApi", __name__)

# 操作mysql CRUD; cudData(query, value) return {"ok":True}成功;
# readData(query, value=None) return 查詢資料 {"error"}錯誤
mysql = Sqlmethod()
# 建立簽章
motcAPI = Auth()


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
        allrouteUID.append(stopBusTime[eachstopUID[0]]["RouteUID"])
        # 把routeUID放進returnData["data"][0]["routedata"] 當KEY
        # 整理estimateStatus狀態
        # estimatetime不為-1，表示有正確倒數秒數，取無條件進位分鐘數；取站牌狀態
        estimateTime = stopBusTime[eachstopUID[0]]["EstimateTime"]
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
    print(f"AIP time: {t2-t1}")
    print(f"Clena time: {t3-t2}")
    return jsonify(returnData), 200


@cache.cached(timeout=15, key_prefix="stop_estimate_time")
def get_stop_estimate_time():
    from requests import request

    # Access data from MOTC ptx
    req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Taipei?$select=StopUID%2C%20RouteUID%2C%20Direction%2C%20EstimateTime%2C%20StopStatus&$format=JSON"
    response = request("get", req_url, headers=motcAPI.authHeader())
    response = response.json()
    stopBusTime = dict()
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
    return stopBusTime


# # 這個function 拆開
# 1.get data
# 2.build data
# # def getEstimatetime():
# #     # 由資料庫取出所需資料，stopstatus 0正常 1未發車 2交管不停靠 3末班車已過 4今日未營運
# #     latitude = request.args.get("latitude")
# #     longitude = request.args.get("longitude")
# #     selectSql = "SELECT (SELECT stopname_tw FROM stationinfo WHERE stationUID = c.stationUID), (SELECT stopname_en \
# #         FROM stationinfo WHERE stationUID = c.stationUID), a.direction, a.estimatetime, a.stopstatus, b.routename_tw, \
# #         b.routename_en, b.depname_tw, b.depname_en, b.destname_tw, b.destname_en FROM stopwaittime AS a JOIN busroute AS \
# #         b USING(routeUID) JOIN stopofstation AS c USING(stopUID) WHERE (SELECT coordinate FROM stationinfo WHERE \
# #         stationUID = c.stationUID) = POINT(%s, %s)"
# #     selectValue = (latitude, longitude)
# #     result = mysql.readData(selectSql, selectValue)
# #     if "error" in result or len(result) == 0:
# #         response = make_response(jsonify(result), 500)
# #         return response
# #     returnData = dict()
# #     returnData["data"] = []
# #     stopname = {
# #         "stopname": {
# #             "tw": result[0][0],
# #             "en": result[0][1]
# #         }
# #     }
# #     returnData["data"].append(stopname)
# #     routedata = {
# #         "routedata":[]
# #     }
# #     returnData["data"].append(routedata)
# #     for eachRow in result:
# #         temp = {
# #             "routename": {
# #                 "tw": eachRow[5],
# #                 "en": eachRow[6]
# #             }
# #         }
# #         # direction = 0 為去程，direction = 1 為返程
#             depname_tw, depname_en, destname_tw, destname_en =(eachRow[9], eachRow[10], eachRow[7], eachRow[8]) if eachRow[2] == 1 else (eachRow[7], eachRow[8], eachRow[9], eachRow[10])
# #         if eachRow[2] == 1:
# #             temp["depdestname"] = {
# #                 "depname_tw": eachRow[9],
# #                 "depname_en": eachRow[10],
# #                 "destname_tw": eachRow[7],
# #                 "destname_en": eachRow[8]
# #             }
# #         else:
# #             temp["depdestname"] = {
# #                 "depname_tw": eachRow[7],
# #                 "depname_en": eachRow[8],
# #                 "destname_tw": eachRow[9],
# #                 "destname_en": eachRow[10]
# #             }
# #         # estimatetime不為-1，表示有正確倒數秒數，取無條件進位分鐘數
# #         if eachRow[3] != -1:
# #             # 若小於30秒顯示進站中
#                 estimateStatus = "進站中" if eachRow[3] <= 60 else str(ceil(eachRow[3]/60)) + "分"
# #             if eachRow[3] <= 30:
# #                 estimateStatus = "進站中"
# #             else:
# #                 estimateStatus = str(ceil(eachRow[3]/60)) + "分"
# #         else:
# #             # stopstatus 0正常 1未發車 2交管不停靠 3末班車已過 4今日未營運
# #               stopstatusmap={1:"未發車", 2:"交管不停靠", 3:"末班車已過", 4:"今日未營運"}
#                 estimateStatus = stopstatusmap.get(eachRow[4])
# #             if eachRow[4] == 1:
# #                 estimateStatus = "未發車"
# #             elif eachRow[4] == 2:
# #                 estimateStatus = "交管不停靠"
# #             elif eachRow[4] == 3:
# #                 estimateStatus = "末班車已過"
# #             elif eachRow[4] == 4:
# #                 estimateStatus = "今日未營運"
# #         temp["estimateStatus"] = estimateStatus
#             temp = {
#                 "routename": {
#                     "tw": eachRow[5],
#                     "en": eachRow[6]
#                 },
#                 "estimateStatus": estimateStatus,
#                 "depdestname": {
#                     "depname_tw": depname_tw,
#                     "depname_en": depname_en,
#                     "destname_tw": destname_tw,
#                     "destname_en": destname_en
#                 },

#             }
# #         returnData["data"][1]["routedata"].append(temp)
# #     return jsonify(returnData), 200

# # while True:
# #     # Insert data into table stopwaittime
# #     req_rul = "https://ptx.transportdata.tw/MOTC/v2/Bus/EstimatedTimeOfArrival/City/Taipei?$select=StopUID%2C%20RouteUID%2C%20Direction%2C%20EstimateTime%2C%20StopStatus&$format=JSON"
# #     response = request("get", req_rul, headers = motcAPI.authHeader())
# #     response = response.json()
# #     insertEstimated = []
# #     t1 = time.time()
# #     for eachRow in response:
# #         if "EstimateTime" not in eachRow:
# #             eachRow["EstimateTime"] = -1
# #         tempTuple = (eachRow["StopUID"], eachRow["RouteUID"], eachRow["Direction"], eachRow["EstimateTime"], eachRow["StopStatus"])
# #         insertEstimated.append(tempTuple)
# #     insertSql = "INSERT INTO stopwaittime (stopUID, routeUID, direction, estimatetime, stopstatus) VALUES (%s, %s, %s, %s, %s)"
# #     # 將上次表格資料清空後新增資料
# #     mysql.tableDBControl("TRUNCATE stopwaittime")
# #     t3 = time.time()
# #     mysql.cudData(insertSql, insertEstimated)

# #     t2 = time.time()
# #     print (t2-t1)
# #     print (t2-t3)
# #     time.sleep(15)
