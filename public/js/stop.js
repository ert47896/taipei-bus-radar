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
    // 繪製地圖
    renderMap: function (lat, lng) {
        // 設定地圖參數
        this.mymap = L.map("mapId").setView([lat, lng], 14);
        // 套用maps terrain圖層
        L.tileLayer('https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg', {
            attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href=\
            "http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">\
            OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
            maxZoom: 18
        }).addTo(this.mymap);
    }
}
// Controllers
let controllers = {
    // 此站牌緯度
    latitude: null,
    // 此站牌經度
    longitude: null,
    // 初始化
    init: function () {
        // 取得站牌經緯度
        const urlPath = (window.location.pathname).split("/");
        this.latitude = urlPath[urlPath.length - 2];
        this.longitude = urlPath[urlPath.length - 1];
        // 初始化地圖
        views.renderMap(this.latitude, this.longitude);
        // 顯示時間
        this.timeNow();
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
    }
}
controllers.init();     // 載入頁面初始化