// Models
let models = {
    // 存放API回復資料
    data: null,
    // 以fetch對API索取資料
    accessAPI: function (url) {
        return fetch(url).then((response) => {
            return response.json();
        }).then((result) => {
            this.data = result;
        });
    }
}
// Views
let views = {
    // 設定路線標題顏色
    routeColor: [["一般公車", "#ed8d74"], ["幹線公車", "#DEC3E1"], ["捷運紅線接駁公車", "#ff939b"],
    ["捷運藍線接駁公車", "#aee8d2"], ["捷運綠線接駁公車", "#BEEB9F"], ["捷運棕線接駁公車", "#CCAE91"],
    ["通勤公車", "#D4E0F9"], ["市民小巴", "#FFCCCB"], ["小", "#B1FF91"], ["觀光巴士", "#BBD5F2"]],
    // 繪製路線資料
    renderBus: function (routeData) {
        // 初始化main物件為空白
        const mainDOM = document.querySelector("main");
        mainDOM.innerHTML = "";
        this.routeColor.forEach((eachRoute) => {
            // 檢查改種類路線有資料才顯示分類框
            if (routeData[eachRoute[0]].length > 0) {
                // 建立section部分，放各路線資料
                const sectionDOM = document.createElement("section");
                sectionDOM.classList.add("routeType");
                mainDOM.appendChild(sectionDOM);
                // 建立該路線標題(設定背景顏色 路線名稱)
                const routeTypeDOM = document.createElement("div");
                routeTypeDOM.classList.add("generalType");
                routeTypeDOM.style.background = eachRoute[1];
                routeTypeDOM.textContent = eachRoute[0];
                sectionDOM.appendChild(routeTypeDOM);
                // 建立ul物件
                const ulDOM = document.createElement("ul");
                ulDOM.classList.add("routeList");
                sectionDOM.appendChild(ulDOM);
                // 建立各路線名稱
                routeData[eachRoute[0]].forEach((eachName) => {
                    const liDOM = document.createElement("li");
                    liDOM.textContent = eachName;
                    ulDOM.appendChild(liDOM);
                    // 建立各路線超連結(.target = "_blank"開啟新分頁)
                    const hyperDOM = document.createElement("a");
                    hyperDOM.href = "/route/" + eachName;
                    hyperDOM.target = "_blank";
                    const spanDOM = document.createElement("span");
                    spanDOM.classList.add("routeUrlLink");
                    hyperDOM.appendChild(spanDOM);
                    liDOM.appendChild(hyperDOM);
                });
            };
        });
    },
    renderNullData: function (data) {
        // 初始化main物件為空白
        const mainDOM = document.querySelector("main");
        mainDOM.innerHTML = "";
        const textDOM = document.createElement("div");
        textDOM.classList.add("resultText");
        textDOM.textContent = data;
        mainDOM.appendChild(textDOM);
    }
}
// Controllers
let controllers = {
    // 初始化
    init: function () {
        // window.location.origin = 主機名稱
        models.accessAPI(window.location.origin + "/api/routes?keyword=").then(() => {
            views.renderBus(models.data.data);
            // 註冊標題點擊及搜尋監聽
            this.routeTitleListener();
            this.searchListener();
        });
    },
    // 標題點擊監聽
    routeTitleListener: function () {
        const routeDOMList = document.querySelectorAll(".routeType");
        for (let i = 0; i < routeDOMList.length; i++) {
            routeDOMList[i].children[0].addEventListener("click", function () {
                routeDOMList[i].children[1].classList.toggle("itemHidden");
            });
        };
    },
    // 搜尋監聽
    searchListener: function () {
        const searchButton = document.querySelector(".searchBtn");
        searchButton.addEventListener("click", function () {
            // 接收查詢關鍵字
            const keyword = document.getElementById("keyword").value;
            models.accessAPI(window.location.origin + "/api/routes?keyword=" + keyword).then(() => {
                // 查無資料
                if (models.data.data === "查無路線資料") {
                    views.renderNullData(models.data.data);
                } else {
                    // 有資料顯示結果
                    views.renderBus(models.data.data);
                    // 註冊標題點擊監聽
                    controllers.routeTitleListener();
                };
            });
        });
    }
}
controllers.init();     // 載入頁面初始化