from flask import Blueprint, jsonify, request
from module.mysqlmethods import Sqlmethod
from module.cache import cache

routesApi = Blueprint("routesApi", __name__)

# 操作mysql CRUD; cudData(query, value) return {"ok":True}成功;
# readData(query, value=None) return 查詢資料 {"error"}錯誤
mysql = Sqlmethod()


@routesApi.route("/routes", methods=["GET"])
def get_routedata():
    # Access data from mysql
    keyword = request.args.get("keyword")
    selectSql = f"SELECT routename_tw FROM busroute WHERE routename_tw LIKE '%{keyword}%' ORDER BY routename_tw"
    result = mysql.readData(selectSql)
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
