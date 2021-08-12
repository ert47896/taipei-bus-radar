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
    // 圖層變數
    mymap: null,
    // 使用者選擇位置marker變數
    usermarker: null,
    // 記錄使用者是否為第一次點擊地圖
    firstclick: true,
    // stop icon變數
    stopIcon: null,
    // 初始化自訂icons
    initStopIcon: function () {
        // 車站icon
        let stopphoto = L.Icon.extend({
            options: { iconSize: [28, 28] }
        });
        this.stopIcon = new stopphoto({ iconUrl: "/image/bus_stop.png" });
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
        // 設定比例尺(取消英里、顯示位置調為右下角)
        L.control.scale({ imperial: false, position: "bottomright" }).addTo(this.mymap);
    },
    // 顯示使用者點擊位置(地圖與文字)並記錄經緯度
    showLocation: function () {
        this.mymap.on("click", function (e) {
            // e is an event object (MouseEvent in this case)
            // 如果已存在marker先移除
            if (views.usermarker) {
                views.mymap.removeLayer(views.usermarker);
            };
            views.usermarker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(views.mymap);
            views.usermarker.bindTooltip("欲查詢位置", { permanent: true, direction: "right" });
            // 畫面移動到所點擊位置
            views.flyToSite([e.latlng.lat, e.latlng.lng], 18);
            // 將使用者欲查詢位置以文字顯示
            // 判斷是否為第一次點擊地圖，若為第一次先顯示網頁標籤內容
            if (views.firstclick) {
                const searchLocation = document.querySelector(".hiddenElement");
                searchLocation.classList.add("selectLocation");
                searchLocation.classList.remove("hiddenElement");
                views.firstclick = null;
            };
            // 更新欲查詢地點資訊
            let longitudeDOM = document.getElementById("longitude");
            longitudeDOM.textContent = e.latlng.lng;
            let latitudeDOM = document.getElementById("latitude");
            latitudeDOM.textContent = e.latlng.lat;
            // 更新使用者欲查詢位置經緯度
            controllers.latitudeSelect = e.latlng.lat;
            controllers.longitudeSelect = e.latlng.lng;
        });
    },
    // 地圖顯示使用者位置
    showUserLocation: function () {
        this.mymap.locate({ setView: true });
    },
    // 請使用者再次確認輸入地址資料
    renderUserCheck: function () {
        const errorAddress = document.querySelector(".errorAddress");
        errorAddress.textContent = "請再次確認所輸入資訊";
    },
    // 顯示查詢結果
    renderResult: function (data) {
        // 清空地圖標記(如果有)，停止點擊監聽
        if (views.usermarker) {
            views.mymap.removeLayer(views.usermarker);
        };
        this.mymap.off("click");
        // 以lat lng畫半徑300公尺圓
        const circle = L.circle([data.selectLat, data.selectLng], { color: "#e60e14", fillColor: "#fbb7b9", fillOpacity: 0.3, radius: 300 }).addTo(this.mymap);
        // 顯示使用者查詢位置marker，並移動地圖至該處
        const searchLocation = L.marker([data.selectLat, data.selectLng]).addTo(this.mymap);
        this.flyToSite(searchLocation.getLatLng(), 17);
        // 清空右側面板資料，填入搜尋結果(經緯度or地址)
        const searchSideDOM = document.querySelector(".searchSide");
        searchSideDOM.innerHTML = "";
        const searchResultDOM = document.createElement("section");
        searchResultDOM.classList.add("searchType");
        searchSideDOM.appendChild(searchResultDOM);
        const titleDOM = document.createElement("div");
        titleDOM.classList.add("searchContent");
        titleDOM.textContent = "查詢位置";
        searchResultDOM.appendChild(titleDOM);
        if (data.method === "latlng") {
            const lngDOM = document.createElement("div");
            lngDOM.classList.add("searchContent");
            lngDOM.textContent = "經度：" + data.selectLng;
            const latDOM = document.createElement("div");
            latDOM.classList.add("searchContent");
            latDOM.textContent = "緯度：" + data.selectLat;
            searchResultDOM.appendChild(lngDOM);
            searchResultDOM.appendChild(latDOM);
        } else {
            const addressDOM = document.createElement("div");
            addressDOM.classList.add("searchContent");
            addressDOM.textContent = "地址：" + data.locationData;
            searchResultDOM.appendChild(addressDOM);
        };
        // 站牌資訊填入地圖及右側面板
        // 查無資料
        if (data.stops === "無鄰近站牌資料") {
            const noDataDOM = document.createElement("div");
            noDataDOM.classList.add("searchTitle");
            noDataDOM.textContent = "查無鄰近站牌資料";
            searchSideDOM.appendChild(noDataDOM);
        } else {
            const stopDataDOM = document.createElement("section");
            stopDataDOM.classList.add("stopData");
            searchSideDOM.appendChild(stopDataDOM);
            for (let i = 0; i < data.stops.length; i++) {
                // 各站牌資料div
                const eachStopDOM = document.createElement("div");
                eachStopDOM.classList.add("eachStopData");
                stopDataDOM.appendChild(eachStopDOM);
                // 編號
                const indexDOM = document.createElement("div");
                indexDOM.classList.add("stopIndex");
                indexDOM.textContent = i + 1;
                eachStopDOM.appendChild(indexDOM);
                // 站名
                const nameDOM = document.createElement("div");
                nameDOM.classList.add("stopName");
                nameDOM.textContent = data.stops[i].stopname_tw;
                eachStopDOM.appendChild(nameDOM);
                // 距離
                const distanceDOM = document.createElement("div");
                distanceDOM.classList.add("stopDistance");
                let distanceString = "距離"
                if (data.stops[i].distance < 100) {
                    distanceString = "距離 "
                }
                distanceDOM.textContent = distanceString + data.stops[i].distance + "公尺";
                eachStopDOM.appendChild(distanceDOM);
                // 超連結
                const hyperStop = document.createElement("a");
                hyperStop.href = "/stop/" + data.stops[i].stopname_tw + "/" + data.stops[i].latitude + "/" + data.stops[i].longitude;
                hyperStop.target = "_blank";
                const spanDOM = document.createElement("span");
                spanDOM.classList.add("stopUrlLink");
                hyperStop.appendChild(spanDOM);
                eachStopDOM.appendChild(hyperStop);
                // 地圖 stop markers
                let stopmarker = L.marker([data.stops[i].latitude, data.stops[i].longitude], { icon: this.stopIcon }).addTo(this.mymap);
                stopmarker.bindTooltip((i + 1).toString(), { permanent: true, direction: "top", className: "map-stop-index", offset: [2, -10] });
                stopmarker.bindPopup(data.stops[i].stopname_tw + "<br>" + "地址: " + data.stops[i].address);
                // 點擊站牌移動到該站位置
                stopmarker.on("click", () => {
                    this.flyToSite(stopmarker.getLatLng(), 18);
                });
            };
        };
    },
    // 地圖中心移動到指定位置
    flyToSite: function (latlng, zoomvalue) {
        this.mymap.flyTo(latlng, zoomvalue);
    }
}
// Controllers
let controllers = {
    // 使用者選擇位置緯度
    latitudeSelect: null,
    // 使用者選擇位置經度
    longitudeSelect: null,
    // 初始化
    init: function () {
        views.renderMap(25.046387, 121.516950);
        // 初始化stop Icon
        views.initStopIcon();
        views.showLocation();
        this.searchByLatLng();
        this.searchByAddress();
        this.timeNow();
        this.userLocation();
    },
    // 監聽使用者點擊 地圖選擇點位的"開始搜尋"按鈕
    searchByLatLng: function () {
        const latlngSearch = document.getElementById("method1");
        latlngSearch.addEventListener("click", function () {
            models.getAPI(window.location.origin + "/api/stops?method=latlng&keyword=" + controllers.latitudeSelect + "," + controllers.longitudeSelect).then(() => {
                views.renderResult(models.data.data[0]);
            });
        });
    },
    // 監聽使用者點擊 地址搜尋方式的"開始搜尋"按鈕
    searchByAddress: function () {
        const addressSearch = document.getElementById("method2");
        addressSearch.addEventListener("click", function () {
            // 接收查詢地址
            const address = document.getElementById("keyword").value;
            // 針對查詢地址內容作初步判斷(字串長度小於6拒絕查詢)
            if (address.length < 7) {
                views.renderUserCheck();
            } else {
                models.getAPI(window.location.origin + "/api/stops?method=address&keyword=" + address).then(() => {
                    views.renderResult(models.data.data[0]);
                });
            };
        });
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
    // 監聽使用者位置按鈕
    userLocation: function () {
        const locationBtn = document.querySelector(".locationBtn");
        locationBtn.addEventListener("click", () => {
            views.showUserLocation();
        });
    }
}
controllers.init();     // 載入頁面初始化