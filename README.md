# [Taipei Bus Radar](https://taipeilife.site/) 台北市公車動態資訊網站

本專案依據[交通部公共運輸資訊服務平台](https://ptx.transportdata.tw/MOTC)資料建置，功能包括：
* 顯示營運公車位置及行駛資訊
* 依據使用者所輸入目標地點，呈現鄰近站牌資訊
* 針對選定站牌顯示經過路線

## Demo
Taipei Bus Radar網站：https://taipeilife.site/<br>

## 使用技術
* 以 Python Flask 框架建立網站
* 使用 MySQL 及 Flask-Caching 儲存資料
* 以第三正規化設計 MySQL 資料庫
* 設定 index 及 foreign key 於 MySQL 資料庫
* 採 RESTful 架構設計網站 API
* 應用 Leaflet 構建網頁地圖
* 運用 Google Geocoding API 進行地址反查經緯度資料
* 部署網站於 AWS EC2 且透由 Nginx 反向代理
* 透由 Let's Encrypt 申請 SSL 憑證實踐 HTTPS

## 系統架構圖
![image](https://user-images.githubusercontent.com/24973056/128721590-5598f6d3-4748-4116-be40-3b8b1ddf0759.png)

## MySQL資料庫架構圖
![image](https://user-images.githubusercontent.com/24973056/128684156-398f38ac-8a9b-481c-afab-85fcabc10225.png)

## 網站導覽
### 首頁

![image](https://user-images.githubusercontent.com/24973056/128689061-ce8041c6-32d0-40c8-a7d0-49b535c60c9e.png)

1. 點擊可移動地圖至使用者位置(需開啟定位權限)
2. 點選顯示公車行駛資訊
3. 點選查看公車預計抵達站牌時間

### 路線資訊頁面

![image](https://user-images.githubusercontent.com/24973056/128700003-0ee92499-1bc1-40e5-92aa-789d02dbd991.png)

1. 點擊顯示業者提供路線簡圖
2. 點擊營運業者網站
3. 點擊切換去程、返程路線及營運車輛資訊
4. 點擊站名地圖移動至該站牌位置

### 搜尋站牌頁面

![image](https://user-images.githubusercontent.com/24973056/128719194-aaff5476-c452-4a99-8d9f-3bd927a1adb7.png)

使用者可點選地圖或輸入地址，查詢目標位置鄰近站牌資訊

### 站牌資訊頁面

![image](https://user-images.githubusercontent.com/24973056/128720468-0d6a8d6e-7ecf-4d9c-aa8b-3952a5c1cc37.png)

1. 點擊顯示經過該站牌路線
2. 於地圖額外顯示該站牌名稱
