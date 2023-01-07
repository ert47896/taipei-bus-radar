// Models
let models = {
    // 存放API回復資料
    data: null,
    // 存放API回復狀態碼
    responseStatus: 0,
    // 以fetch對API索取資料
    getAPI: function (srcUrl) {
        return fetch(srcUrl).then((response) => {
            this.responseStatus = response.status;
            return response.json();
        }).then((result) => {
            this.data = result;
        });
    }
}
// Views
let views = {
    // 圖層變數
    mymap: null,
    // bus icon變數
    orangeBus: null,
    // stop icon變數
    stopIcon: null,
    // bus layer(運用群集套件，spiderfyOnMaxZoom 取消聯結效果，於 zoom 值 18 不要群集)
    buslayer: L.markerClusterGroup({ spiderfyOnMaxZoom: false, disableClusteringAtZoom: 18 }),
    // stop layer
    stoplayer: null,
    // 到站時間面板狀態變數 true有顯示 false未顯示
    estimateTimePanel: false,
    // 呈現站牌資訊緯度
    stopLatitude: null,
    // 呈現站牌資訊經度
    stopLongitude: null,
    // 自訂icons
    initIcons: function () {
        let busIcon = L.Icon.extend({
            options: { iconSize: [22, 22] }
        });
        this.orangeBus = new busIcon({ iconUrl: "/image/orange72.png" });
        let busStop = L.Icon.extend({
            options: { iconSize: [30, 30] }
        });
        this.stopIcon = new busStop({ iconUrl: "/image/bus_stop.png" });
    },
    // 繪製地圖
    renderMap: function (lat, lon) {
        // 設定地圖參數
        this.mymap = L.map("mapId").setView([lat, lon], 17);
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
    // 地圖顯示使用者位置
    showUserLocation: function () {
        this.mymap.locate({ setView: true });
    },
    // 標註公車位置及服務數量
    renderBus: function (data) {
        let totalOperate = 0;
        for (const [key, busData] of Object.entries(data)) {
            busData["OperateBus"].forEach((eachBus) => {
                // Notice: some bus didn't have route name(chinses & english), because of the null data in MySQL
                let marker = L.marker([eachBus["latitude"], eachBus["longitude"]], { icon: this.orangeBus }).bindTooltip(busData["routename"]["tw"] + "<br>" + eachBus["platenumb"]);
                this.buslayer.addLayer(marker);
                // 如果為返程將起訖點互換
                if (eachBus["direction"] === 1) {
                    const temp = busData["depdestname"]["depname_tw"];
                    const tempEnglish = busData["depdestname"]["depname_en"];
                    busData["depdestname"]["depname_tw"] = busData["depdestname"]["destname_tw"];
                    busData["depdestname"]["depname_en"] = busData["depdestname"]["destname_en"];
                    busData["depdestname"]["destname_tw"] = temp;
                    busData["depdestname"]["destname_en"] = tempEnglish;
                }
                marker.bindPopup(busData["routename"]["tw"] + "<br>" + busData["depdestname"]["depname_tw"] + " 往 " +
                    busData["depdestname"]["destname_tw"] + "<br>" + busData["routename"]["en"] + "<br>" + busData["depdestname"]["depname_en"] +
                    " To " + busData["depdestname"]["destname_en"] + "<br>" + "車牌(Platenumber): " + eachBus["platenumb"] + "<br>" +
                    "目前時速(Speed): " + eachBus["speed"] + " km/hr", { className: "icon-click-show" });
                totalOperate += 1;
            });
        };
        this.mymap.addLayer(this.buslayer);
        const textDOM = document.querySelector(".totalBusPart");
        textDOM.textContent = totalOperate + " 輛公車行駛中";
    },
    // 刪除前次公車位置
    removeBus: function () {
        this.buslayer.clearLayers();
    },
    // 顯示站牌位置並建立點擊偵測
    renderStop: function (data) {
        this.stoplayer = L.layerGroup().addTo(this.mymap);
        for (let i = 0; i < data.length; i++) {
            let marker = L.marker([data[i]["latitude"], data[i]["longitude"]], { icon: this.stopIcon }).addTo(this.stoplayer);
            marker.bindPopup(data[i]["stopname"]["tw"] + "<br>" + data[i]["stopname"]["en"] + "<br>" + "地址: " + data[i]["address"], { className: "icon-click-show" });
            // 點擊呼叫函式顯示到站時間，且地圖中心設定為車站位置
            marker.on("click", () => {
                controllers.showEstimateTime(marker.getLatLng().lat, marker.getLatLng().lng);
                this.stopLatitude = marker.getLatLng().lat;
                this.stopLongitude = marker.getLatLng().lng;
                this.mymap.flyTo(marker.getLatLng());
            });
        };
        // 圖層放大至17層以上才顯示車站icon
        this.mymap.on("zoomend", () => {
            if (this.mymap.getZoom() < 17) {
                this.mymap.removeLayer(this.stoplayer);
            } else {
                this.mymap.addLayer(this.stoplayer);
            };
        });
    },
    // 顯示剩餘時間面板
    renderEstimateTime: function (data) {
        const asideDOM = document.querySelector("aside");
        // 已存在面板，清空資料；未存在面板賦予<aside> tag class並宣告面板存在
        if (this.estimateTimePanel === true) {
            asideDOM.innerHTML = "";
        } else {
            this.estimateTimePanel = true;
            asideDOM.classList.add("estimateTimeSide");
        }
        // 建立刪除符號
        const deleteBtn = document.createElement("div");
        deleteBtn.classList.add("closeBtn");
        asideDOM.appendChild(deleteBtn);
        // 建立站牌名稱欄
        const titleDOM = document.createElement("section");
        titleDOM.classList.add("stopTitle");
        asideDOM.appendChild(titleDOM);
        // 於站牌名稱欄填入內容
        for (const [key, routename] of Object.entries(data[1]["stopname"])) {
            const stopnametwDOM = document.createElement("div");
            stopnametwDOM.textContent = routename;
            titleDOM.appendChild(stopnametwDOM);
        };
        // 建立站牌超連結
        const stopHyper = document.createElement("a");
        stopHyper.href = "/stop/" + data[1]["stopname"].tw + "/" + this.stopLatitude + "/" + this.stopLongitude;
        stopHyper.target = "_blank";
        const spanElement = document.createElement("span");
        spanElement.classList.add("domUrlLink");
        stopHyper.appendChild(spanElement);
        titleDOM.appendChild(stopHyper);
        Object.entries(data[0]["routedata"]).forEach(([key, routevalue]) => {
            const routeDataDOM = document.createElement("section");
            routeDataDOM.classList.add("estimateTimeContainer");
            asideDOM.appendChild(routeDataDOM);
            // 剩餘時間狀態
            const estimateStatusDOM = document.createElement("div");
            estimateStatusDOM.classList.add("estimateTimeStatus");
            estimateStatusDOM.textContent = routevalue.estimateStatus;
            routeDataDOM.appendChild(estimateStatusDOM);
            // 路線資料
            const estimateRouteDOM = document.createElement("div");
            estimateRouteDOM.classList.add("estimateTimeRoute");
            routeDataDOM.appendChild(estimateRouteDOM);
            const routeTW = routevalue.routename.tw + " - " + routevalue.depdestname.depname_tw + " 往 " + routevalue.depdestname.destname_tw;
            const routeTWDOM = document.createElement("div");
            routeTWDOM.textContent = routeTW;
            estimateRouteDOM.appendChild(routeTWDOM);
            const routeEN = routevalue.routename.en + " - " + routevalue.depdestname.depname_en + " To " + routevalue.depdestname.destname_en;
            const routeENDOM = document.createElement("div");
            routeENDOM.textContent = routeEN;
            estimateRouteDOM.appendChild(routeENDOM);
            // 路線超連結
            const routeHyper = document.createElement("a");
            routeHyper.href = "/route/" + routevalue.routename.tw;
            routeHyper.target = "_blank";
            const spanHyper = document.createElement("span");
            spanHyper.classList.add("domUrlLink");
            routeHyper.appendChild(spanHyper);
            estimateRouteDOM.appendChild(routeHyper);
            // 針對進站中與2分鐘內換色
            if (routevalue.estimateStatus === "進站中") {
                estimateStatusDOM.classList.add("busapproach");
                estimateRouteDOM.classList.add("estimateTimeRoute-busapproach");
            } else if (routevalue.estimateStatus === "2分" || routevalue.estimateStatus === "1分") {
                estimateStatusDOM.classList.add("lesstwominutes");
                estimateRouteDOM.classList.add("estimateTimeRoute-lesstwominutes");
            }
        });
    },
    // 隱藏剩餘時間面板
    hideEstimateTime: function () {
        // 清除<aside>內容
        const asideDOM = document.querySelector(".estimateTimeSide");
        asideDOM.innerHTML = "";
        asideDOM.classList.remove("estimateTimeSide");
        this.estimateTimePanel = false;
    }
}
// Controllers
let controllers = {
    // 剩餘時間面板更新變數
    renewPanelInterval: null,
    // 初始化
    init: function () {
        views.renderMap(25.046387, 121.516950);
        views.initIcons();
        this.showBusLocation();
        this.showStop();
        this.renewBusLocation();
        this.timeNow();
        this.userLocation();
    },
    // 顯示公車位置
    showBusLocation: function () {
        // window.location.origin = 主機名稱
        models.getAPI(window.location.origin + "/api/buslocation").then(() => {
            views.renderBus(models.data.data);
        });
    },
    // 顯示站牌
    showStop: function () {
        models.getAPI(window.location.origin + "/api/stoplocation").then(() => {
            views.renderStop(models.data.data);
        });
    },
    // 15秒刪除前次公車位置，並更新
    renewBusLocation: function () {
        setInterval(() => {
            models.getAPI(window.location.origin + "/api/buslocation").then(() => {
                views.removeBus();
                views.renderBus(models.data.data);
            });
        }, 15000);
    },
    // 繪製剩餘時間面板，建立刪除鍵監聽、時間面板存在監測
    showEstimateTime: function (latitude, longitude) {
        models.getAPI(window.location.origin + "/api/estimatetime?" + "latitude=" + latitude + "&longitude=" + longitude).then(() => {
            // 如果面板已顯示，隱藏剩餘時間面板且停止15秒更新，繪製新面板
            if (views.estimateTimePanel === true) {
                clearInterval(this.renewPanelInterval);
            }
            views.renderEstimateTime(models.data.data);
            this.deleteBtnControl();
            this.renewPanelData(latitude, longitude);
        });
    },
    // 建立面板刪除鍵監聽，刪除面板並停止15秒更新
    deleteBtnControl: function () {
        const deleteBtn = document.querySelector(".closeBtn");
        deleteBtn.addEventListener("click", () => {
            views.hideEstimateTime();
            clearInterval(this.renewPanelInterval);
        });
    },
    // 15秒刪除前次面板資料，並更新資料，繪製新面板建立刪除鍵監聽
    renewPanelData: function (latitude, longitude) {
        this.renewPanelInterval = setInterval(() => {
            if (views.estimateTimePanel === true) {
                models.getAPI(window.location.origin + "/api/estimatetime?" + "latitude=" + latitude + "&longitude=" + longitude).then(() => {
                    views.renderEstimateTime(models.data.data);
                    this.deleteBtnControl();
                });
            };
        }, 15000);
    },
    // 顯示現在時間
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
    // 使用者位置按鈕監聽
    userLocation: function () {
        const locationButton = document.querySelector(".locationBtn");
        locationButton.addEventListener("click", () => {
            views.showUserLocation();
        });
    }
}
controllers.init();     // 載入頁面初始化