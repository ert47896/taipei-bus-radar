// Models
let models = {
    // 存放API回復資料
    data: null,
    // 以fetch對API索取資料
    getAPI: function (APIurl) {
        return fetch(APIurl).then((response) => {
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
    // 前次的站牌direction資料
    stopDirectionPre: null,
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
    renderMap: function (lat, lon) {
        // 設定地圖參數
        this.mymap = L.map("mapId").setView([lat, lon], 12);
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
    // 繪製路線圖
    renderBusLine: function (lineList) {
        // 少數路線交通部未提供路線資料
        if (lineList === "未提供路線資料") {
            // 新增"未提供路線資料"提醒
            const routeTitleDiv = document.querySelector(".routeTitle");
            const nodataSpan = document.createElement("span");
            nodataSpan.textContent = " (未提供路線資料)";
            nodataSpan.classList.add("noRouteData");
            routeTitleDiv.appendChild(nodataSpan);
        } else {
            const routeLine = L.polyline(lineList, { color: "#d36ca7" }).addTo(this.mymap);
        };
    },
    // 標註路線資料
    renderRouteTitle: function (data) {
        // 父層DOM
        const routeTitleDOM = document.querySelector(".routeTitle");
        // 建立路線名稱及資料超連結
        const hyperRouteTitle = document.createElement("a");
        hyperRouteTitle.classList.add("hyperTitle");
        hyperRouteTitle.href = data.routeimgurl;
        hyperRouteTitle.target = "_blank";
        hyperRouteTitle.textContent = data.routename_tw;
        routeTitleDOM.append(hyperRouteTitle);
        // 建立營運業者資料
        const routeSubTitleDOM = document.querySelector(".routeSubTitle");
        // 可能有多個營運業者
        data.operator.forEach((eachOperator) => {
            const spanDOM = document.createElement("span");
            const hyperDOM = document.createElement("a");
            spanDOM.appendChild(hyperDOM);
            hyperDOM.classList.add("hyperTitle");
            hyperDOM.href = eachOperator.webpage;
            hyperDOM.target = "_blank";
            hyperDOM.textContent = eachOperator.oname_tw;
            routeSubTitleDOM.appendChild(spanDOM);
        });
        // 路線去程往 迄點；返程往 起點
        const depdestDOMList = document.querySelectorAll(".depdestTitle");
        const depSpan = document.createElement("div");
        depSpan.textContent = data.destname_tw;
        const destSpan = document.createElement("div");
        destSpan.textContent = data.depname_tw;
        depdestDOMList[0].appendChild(depSpan);
        depdestDOMList[1].appendChild(destSpan);
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
        // 確認本次站牌direction改變清空前次資料
        if (this.stopDirectionPre !== controllers.stopDirectionNow) {
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
                // 確認本次站牌direction改變更新站牌marker資料
                if (this.stopDirectionPre !== controllers.stopDirectionNow) {
                    // 標註車站序
                    let marker = L.marker([data[index]["latitude"], data[index]["longitude"]], { icon: this.stopIcon }).bindTooltip((index + 1).toString(), { permanent: true, direction: "top", className: "map-stop-sequence", offset: [2, -8] }).addTo(this.stoplayer);
                    marker.bindPopup(data[index]["stopname"] + "<br>" + "地址: " + data[index]["address"], { className: "icon-click-show" });
                    // 車站被點擊設定為地圖中心
                    marker.on("click", () => {
                        this.flyToSite(marker.getLatLng(), 17);
                    });
                    this.stopMarks.push(marker);
                };
                // 建立事件監聽-點擊各站牌資訊畫面移動到該站位置
                controllers.stopEvent(eachStopDOM, index);
            };
        };
        // 更新目前地圖上站牌direction
        this.stopDirectionPre = controllers.stopDirectionNow;
    },
    flyToSite: function (latlng, zoomvalue) {
        this.mymap.flyTo(latlng, zoomvalue);
    }
}
// Controllers
let controllers = {
    // routeStatus資料更新變數
    renewRouteStatusInterval: null,
    // 起始畫面預設direction=0 顯示去程資料
    initDirection: 0,
    // 目前更新route status data的direction
    stopDirectionNow: null,
    // 初始化
    init: function () {
        views.renderMap(25.046387, 121.516950);
        // 初始化icons, group layer
        views.initMapItems();
        // 讀取routeAPI資料並繪製
        // 以decodeURI()將url子路徑解碼(部分路線非全數字)
        models.getAPI(window.location.origin + "/api" + decodeURI(window.location.pathname)).then(() => {
            views.renderRouteTitle(models.data.data);
            views.renderBusLine(models.data.data.lineLatLon);
        });
        // 讀取routestatus資料並繪製 (direction=0 去程)
        this.showRoutestatusData(this.initDirection);
        // 建立去程 返程按鈕監聽
        this.depreturnButton();
        // 建立15秒更新routestatus資料 (direction=0 去程)
        this.renewRouteStatus(this.initDirection);
        // 顯示時間
        this.timeNow();
    },
    // 讀取此路線routestatus資料(direction=0 去程 direction=1 返程)並繪製，建立15秒更新
    showRoutestatusData: function (direction) {
        // 將這次的direction存下來提供views部分判斷要不要重繪地圖站牌資料
        this.stopDirectionNow = direction;
        // 取得routename
        const urlPathname = (window.location.pathname).split("/");
        const routename = urlPathname[urlPathname.length - 1];
        models.getAPI(window.location.origin + "/api/routestatus/" + decodeURI(routename)).then(() => {
            const dataset = models.data["data"][direction];
            // 繪製公車於地圖位置
            views.renderBus(dataset["OperateBus"]);
            // 繪製車站相關資料與公車在車站位置            
            views.renderStopData(dataset["StopsData"]);
        });
    },
    // 去程點擊 返程點擊監聽
    depreturnButton: function () {
        const buttons = document.querySelectorAll(".depdestTitle");
        const depBtn = buttons[0];
        const returnBtn = buttons[1];
        depBtn.addEventListener("click", () => {
            // 刪除前次建立的15秒更新
            clearInterval(this.renewRouteStatusInterval);
            // 檢查按鈕背景
            if (depBtn.classList.contains("depdestTitle-show") === false) {
                depBtn.classList.add("depdestTitle-show");
                returnBtn.classList.remove("depdestTitle-show");
            };
            // 先建立畫面接續建立15秒更新
            this.showRoutestatusData(0);
            this.renewRouteStatus(0);
        });
        returnBtn.addEventListener("click", () => {
            // 刪除前次建立的15秒更新
            clearInterval(this.renewRouteStatusInterval);
            if (returnBtn.classList.contains("depdestTitle-show") === false) {
                returnBtn.classList.add("depdestTitle-show");
                depBtn.classList.remove("depdestTitle-show");
            };
            this.showRoutestatusData(1);
            this.renewRouteStatus(1);
        });
    },
    renewRouteStatus: function (direction) {
        this.renewRouteStatusInterval = setInterval(() => {
            this.showRoutestatusData(direction);
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
    stopEvent: function (objectDOM, index) {
        objectDOM.addEventListener("click", () => {
            views.flyToSite(views.stopMarks[index].getLatLng(), 17);
        });
    }
}
controllers.init();     // 載入頁面初始化