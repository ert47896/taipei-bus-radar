// Models
let models = {
    // 存放API回復資料
    data: null,
    // 以fetch對API讀取資料
    getAPI: function (urlAPI) {
        return fetch(urlAPI).then((response) => {
            return response.json();
        }).then((result) => {
            this.data = result;
        });
    }
}
// Views
let views = {
    // 地圖變數
    mymap: null,
    // 路線線型變數
    routeLine: null,
    // bus icon變數
    busIcon: null,
    // stop icon變數
    stopIcon: null,
    // bus layer
    buslayer: null,
    // stop layer
    stoplayer: null,
    // 記錄公車是否有在地圖上
    busonmap: [],
    // 前次的route name
    routeNamePre: null,
    // 前次的route 營運方向
    directionPre: null,
    // stop marks
    stopMarks: [],
    // 初始化自訂icons, layer groups
    initMapItems: function () {
        // 公車icon
        let busphoto = L.Icon.extend({
            options: { iconSize: [60, 60] }
        });
        this.busIcon = new busphoto({ iconUrl: "/image/orange72.png" });
        // 車站icon
        let stopphoto = L.Icon.extend({
            options: { iconSize: [24, 24] }
        });
        this.stopIcon = new stopphoto({ iconUrl: "/image/bus_stop.png" });
        // layer groups
        this.buslayer = L.layerGroup().addTo(this.mymap);
        this.stoplayer = L.layerGroup().addTo(this.mymap);
    },
    // 繪製地圖
    renderMap: function (lat, lng) {
        // 設定地圖參數
        this.mymap = L.map("mapId").setView([lat, lng], 14);
        // 套用maps terrain圖層
        L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.{ext}', {
            attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href=\
            "http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">\
            OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
            maxZoom: 18,
            subdomains: "abcd",
            ext: "png"
        }).addTo(this.mymap);
        // 設定比例尺(取消顯示英里、顯示位置調為右下角)
        L.control.scale({ imperial: false, position: "bottomright" }).addTo(this.mymap);
    },
    renderNoRoute: function (data) {
        const stopNameDOM = document.querySelector(".stopData");
        // 站牌名稱
        stopNameDOM.textContent = controllers.stopname;
        // 顯示無資料
        const noDataDOM = document.createElement("div");
        noDataDOM.classList.add("noRouteData");
        noDataDOM.textContent = data;
        stopNameDOM.appendChild(noDataDOM);
    },
    renderRouteData: function (data) {
        const stopNameDOM = document.querySelector(".stopData");
        // 站牌名稱
        stopNameDOM.textContent = controllers.stopname;
        // section-allRoute
        const allRouteDOM = document.querySelector(".allRoutes");
        // 建立各路線按鈕
        data.forEach((routedata) => {
            const routeNameDOM = document.createElement("div");
            routeNameDOM.classList.add("routeName");
            if (routedata.direction === 0) {
                routeNameText = routedata.routename + " " + routedata.depname_tw + " 往 " + routedata.destname_tw;
            } else {
                routeNameText = routedata.routename + " " + routedata.destname_tw + " 往 " + routedata.depname_tw;
            };
            routeNameDOM.textContent = routeNameText;
            allRouteDOM.appendChild(routeNameDOM);
            // 針對路線按鈕建立點擊監聽
            controllers.routeEvent(routeNameDOM, routedata.routename, routedata.direction);
        });
    },
    renderBusRoute: function (lineList) {
        // 清空地圖標記(如果有)
        if (this.routeLine) {
            this.mymap.removeLayer(this.routeLine);
        };
        // 少數路線交通部未提供路線資料
        if (lineList === "未提供路線資料") {
            // 顯示"未提供路線資料"
            const asideDOM = document.querySelector(".stopAllRoutes");
            const noRouteDOM = document.createElement("section");
            noRouteDOM.classList.add("noRouteData", "stopData");
            noRouteDOM.textContent = lineList;
            asideDOM.appendChild(noRouteDOM);
        } else {
            this.routeLine = L.polyline(lineList, { color: "#d36ca7" }).addTo(this.mymap);
        };
    },
    // 標註公車位置及服務數量
    renderBus: function (data) {
        // 清空地圖公車
        this.buslayer.clearLayers();
        data.forEach((eachBus) => {
            let marker = L.marker([eachBus["latitude"], eachBus["longitude"]], { icon: this.busIcon }).bindTooltip(eachBus["platenumb"], { direction: "top" }).addTo(this.buslayer);
            marker.bindPopup("車牌(Platenumber): " + eachBus["platenumb"] + "<br>" + "目前時速(Speed): " + eachBus["speed"] + " km/hr", { className: "icon-click-show" });
            // 點擊地圖中心設定為車輛位置
            marker.on("click", () => {
                this.mymap.flyTo(marker.getLatLng(), 15);
            });
            // 將地圖上的公車記錄起來，作為公車在車站位置資料比對(交通部提供公車在車站位置有時會發生該公車於動態資料中查無資訊)
            this.busonmap.push(eachBus["platenumb"]);
        });
    },
    // 標註車站序、繪製車站資料與公車在車站位置
    renderStopData: function (data) {
        // 確認本次route name改變清空前次資料，針對路線名稱一樣透過營運方向確認
        if ((this.routeNamePre !== controllers.routeNameNow) || (this.directionPre !== controllers.directionNow)) {
            // 清空地圖站牌序列、stop marks
            this.stoplayer.clearLayers();
            this.stopMarks = [];
        };
        // 清空車站資料內容
        const articleDOM = document.querySelector(".routeStopAll");
        articleDOM.innerHTML = "";
        // 少數路線返程交通部未提供站點資料
        if (data.length === 0) {
            const routeStopAllDOM = document.querySelector(".routeStopAll");
            const nodataTextDOM = document.createElement("div");
            nodataTextDOM.classList.add("nodataText");
            nodataTextDOM.textContent = "未提供路線資料";
            routeStopAllDOM.appendChild(nodataTextDOM);
        } else {
            for (let index = 0; index < data.length; index++) {
                // 填入車站資料與公車在車站位置
                const eachStopDOM = document.createElement("div");
                eachStopDOM.classList.add("eachStopStatus");
                articleDOM.appendChild(eachStopDOM);
                // 車輛到站狀態、車站序列、車站名稱
                const stopstatusDOM = document.createElement("div");
                stopstatusDOM.classList.add("estimateStatus");
                stopstatusDOM.textContent = data[index]["estimatestatus"];
                // 車輛到站狀態如為進站中，背景色改為紅色
                if (data[index]["estimatestatus"] === "進站中") {
                    stopstatusDOM.classList.add("busComingsoon");
                };
                eachStopDOM.appendChild(stopstatusDOM);
                const stopsequenceDOM = document.createElement("div");
                stopsequenceDOM.classList.add("stopSequence");
                // 交通部給的路線資料sequence部分有錯誤 (例如路線39去程，23下一站跳25)，故以資料index+1方式呈現站序
                stopsequenceDOM.textContent = index + 1;
                eachStopDOM.appendChild(stopsequenceDOM);
                const stopnameDOM = document.createElement("div");
                stopnameDOM.classList.add("stopName");
                stopnameDOM.textContent = data[index]["stopname"];
                eachStopDOM.appendChild(stopnameDOM);
                // 檢查有無公車在該車站
                const buslocationDOM = document.createElement("div");
                buslocationDOM.classList.add("busLocation");
                eachStopDOM.appendChild(buslocationDOM);
                if (data[index]["platenumb"].length > 0) {
                    // 新增車牌資料
                    data[index]["platenumb"].forEach((busplatenum) => {
                        // 檢查車牌有沒有出現在地圖上(交通部提供公車在車站位置有時會發生該公車於動態資料中查無資訊)
                        if (this.busonmap.includes(busplatenum)) {
                            const busplatenumbDOM = document.createElement("div");
                            busplatenumbDOM.classList.add("eachBus");
                            busplatenumbDOM.textContent = busplatenum;
                            buslocationDOM.appendChild(busplatenumbDOM);
                        };
                    });
                };
                // 確認本次route name改變更新地圖站牌marker資料，針對路線名稱一樣透過營運方向確認
                if ((this.routeNamePre !== controllers.routeNameNow) || (this.directionPre !== controllers.directionNow)) {
                    // 標註車站序
                    let marker = L.marker([data[index]["latitude"], data[index]["longitude"]], { icon: this.stopIcon }).addTo(this.stoplayer);
                    // 如該站牌是目標站牌，顯示更詳細資訊
                    if ((data[index]["latitude"] == Number(controllers.latitude)) && (data[index]["longitude"] == Number(controllers.longitude))) {
                        marker.bindTooltip((index + 1).toString() + " " + data[index]["stopname"], { permanent: true, direction: "top", className: "map-stop-select", offset: [2, -8] });
                    } else {
                        marker.bindTooltip((index + 1).toString(), { permanent: true, direction: "top", className: "map-stop-sequence", offset: [2, -8] });
                    }
                    marker.bindPopup(data[index]["stopname"] + "<br>" + "地址: " + data[index]["address"], { className: "icon-click-show" });
                    // 車站被點擊設定為地圖中心
                    marker.on("click", () => {
                        this.flyToSite(marker.getLatLng(), 17);
                    });
                    this.stopMarks.push(marker);
                    // 如果該站牌是搜尋目標更改顏色並顯示站名
                };
                // 建立事件監聽-點擊各站牌資訊畫面移動到該站位置
                controllers.stopClick(eachStopDOM, index);
            };
        };
        // 更新目前地圖上站牌資料的route name與營運方向
        this.routeNamePre = controllers.routeNameNow;
        this.directionPre = controllers.directionNow;
    },
    flyToSite: function (latlng, zoomvalue) {
        this.mymap.flyTo(latlng, zoomvalue);
    },
    // 更新按鈕顏色(原始的移除，被點擊的新增)
    changeButtonColor: function (newDOM) {
        const preSelectDOM = document.querySelector(".route-show");
        preSelectDOM.classList.remove("route-show");
        // 將此按鈕改成被點擊後顏色
        newDOM.classList.add("route-show");
    }
}
// Controllers
let controllers = {
    // 此站牌站名
    stopname: null,
    // 此站牌緯度
    latitude: null,
    // 此站牌經度
    longitude: null,
    // routeStatus資料15秒更新變數
    renewRouteStatusInterval: null,
    // 目前選擇的route name
    routeNameNow: null,
    // 目前選擇的route營運方向
    directionNow: null,
    // 初始化
    init: function () {
        // 取得站牌名 經緯度
        // 以decodeURI()將url中站名解碼
        const urlPath = decodeURI(window.location.pathname).split("/");
        this.latitude = urlPath[urlPath.length - 2];
        this.longitude = urlPath[urlPath.length - 1];
        this.stopname = urlPath[urlPath.length - 3];
        // 建立地圖
        views.renderMap(this.latitude, this.longitude);
        // 初始化icons, group layer
        views.initMapItems();
        // 取得經過該站牌路線資料
        models.getAPI(window.location.origin + "/api/stop?latitude=" + this.latitude + "&longitude=" + this.longitude).then(() => {
            // 無路線經過
            if (models.data.data[0].error) {
                // 繪製無路線經過
                views.renderNoRoute(models.data.data[0].error);
            } else {
                // 繪製經過路線資料
                views.renderRouteData(models.data.data);
                // 初始頁面顯示第一組路線資料
                this.routeNameNow = models.data.data[0].routename;
                this.directionNow = models.data.data[0].direction;
                // 改變按鈕顏色
                const allRouteDOM = document.querySelectorAll(".routeName");
                allRouteDOM[0].classList.add("route-show");
                // 顯示路線資料並建立15秒更新機制
                this.showRouteStatusData(models.data.data[0].routename, models.data.data[0].direction);
                this.renewRouteStatus(models.data.data[0].routename, models.data.data[0].direction);
                // 顯示路線線形資料
                this.showBusRoute(models.data.data[0].routename);
                // 顯示路線資料後地圖位置顯示在該站牌
                views.flyToSite([this.latitude, this.longitude], 15);
            };
        });
        // 顯示時間
        this.timeNow();
    },
    // 建立路線按鈕點擊監聽
    routeEvent: function (routeNameDOM, routeName, direction) {
        routeNameDOM.addEventListener("click", () => {
            // 移除前次路線15秒更新
            clearInterval(this.renewRouteStatusInterval);
            // 更新按鈕顏色
            views.changeButtonColor(routeNameDOM);
            // 讀取routestatus資料並繪製於地圖及右側資訊欄
            this.showRouteStatusData(routeName, direction);
            // 向routeAPI讀取路線線型資料接續繪製於地圖
            this.showBusRoute(routeName);
            // 建立15秒更新routestatus資料
            this.renewRouteStatus(routeName, direction);
        });
    },
    // 讀取路線線型資料接續會至於地圖
    showBusRoute: function (routename) {
        models.getAPI(window.location.origin + "/api/route/" + routename).then(() => {
            views.renderBusRoute(models.data.data.lineLatLon);
        });
    },
    // 讀取routestatus資料並繪製於地圖及右側資訊欄
    showRouteStatusData: function (routeName, direction) {
        // 將此次route name與營運方向儲存提供views判斷更新資料時是否要重繪地圖上站牌資料
        this.routeNameNow = routeName;
        this.directionNow = direction;
        // 向routeAPI讀取路線相關車輛 進站狀態資料
        models.getAPI(window.location.origin + "/api/routestatus/" + routeName).then(() => {
            // 只取用單一方向資料
            const dataSelect = models.data["data"][direction];
            // 繪製公車於地圖位置
            views.renderBus(dataSelect["OperateBus"]);
            // 繪製站牌於地圖 標註站牌相關文字資料與公車所在站牌位置            
            views.renderStopData(dataSelect["StopsData"]);
        });
    },
    // 15秒更新routestatus資料
    renewRouteStatus: function (routeName, direction) {
        this.renewRouteStatusInterval = setInterval(() => {
            this.showRouteStatusData(routeName, direction);
        }, 15000);
    },
    timeNow: function () {
        const dateNow = new Date();
        let hour = dateNow.getHours();
        if (hour < 10) {
            hour = "0" + (hour).toString();
        };
        let minute = dateNow.getMinutes();
        if (minute < 10) {
            minute = "0" + (minute).toString();
        };
        let second = dateNow.getSeconds();
        if (second < 10) {
            second = "0" + (second).toString();
        };
        const timeDOM = document.querySelector(".timePart");
        timeDOM.innerHTML = "";
        timeDOM.textContent = hour + ":" + minute + ":" + second;
        setTimeout("controllers.timeNow()", 1000);
    },
    stopClick: function (clickDOM, index) {
        clickDOM.addEventListener("click", () => {
            views.flyToSite(views.stopMarks[index].getLatLng(), 17);
        });
    }
}
controllers.init();     // 載入頁面初始化