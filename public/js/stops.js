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
    firstclick: true,
    // 繪製地圖
    renderMap: function (lat, lon) {
        // 設定地圖參數
        this.mymap = L.map("mapId").setView([lat, lon], 17);
        // 套用maps terrain圖層
        L.tileLayer('https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg', {
            attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href=\
            "http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">\
            OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
            maxZoom: 18
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
            views.mymap.flyTo([e.latlng.lat, e.latlng.lng], 18);
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
            // API
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
                // API
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