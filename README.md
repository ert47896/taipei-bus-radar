# [Taipei Bus Radar](https://bus.taipeilife.info/) 台北市公車動態資訊網站

本網站依據[交通部公共運輸資訊服務平台](https://ptx.transportdata.tw/MOTC)資料建置，功能包括：
* 顯示營運公車位置及行駛資訊
* 查看公車預計抵達站牌時間
* 提供各營運路線資訊
* 依據使用者所輸入目標地點，呈現鄰近站牌資訊
* 針對選定站牌顯示經過路線

## Demo
Taipei Bus Radar網站：https://bus.taipeilife.info/<br>

## 使用技術
* Python Flask
* 採MVC架構編寫Javascript
* 應用Leaflet構建網頁地圖
* 使用MySQL及Flask-caching儲存資料
* 採RESTful架構設計網站API
* 運用Google Geocoding API進行地址反查經緯度資料
* 部署網站於AWS EC2並運用nginx反向代理
* SSL憑證實踐HTTPS

## 系統架構圖
![image](https://user-images.githubusercontent.com/24973056/128684074-fb6980cc-c33c-4de4-a297-cf6f486c8b92.png)

## MySQL資料庫架構
![image](https://user-images.githubusercontent.com/24973056/128684156-398f38ac-8a9b-481c-afab-85fcabc10225.png)

## 網站導覽
### 首頁

![image](https://user-images.githubusercontent.com/24973056/128689061-ce8041c6-32d0-40c8-a7d0-49b535c60c9e.png)

1. 點擊可移動地圖至使用者位置(需開啟定位權限)
2. 點選顯示公車行駛資訊

![image](https://user-images.githubusercontent.com/24973056/128689559-ede95b95-cc55-4af4-a8e7-6f8de71fade1.png)

3. 點選查看公車預計抵達站牌時間

![image](https://user-images.githubusercontent.com/24973056/128689898-aa9e419f-1294-43b4-93e5-47c984825d4d.png)

### 路線資訊頁面

![image](https://user-images.githubusercontent.com/24973056/128700003-0ee92499-1bc1-40e5-92aa-789d02dbd991.png)

1. 點擊顯示業者提供路線簡圖
2. 點擊營運業者網站
3. 點擊切換去程、返程路線及營運車輛資訊

![image](https://user-images.githubusercontent.com/24973056/128700738-9e108a01-d31c-4b6f-99f2-69dee061f583.png)

4. 點擊站名地圖移動至該站牌位置

### 站牌資訊頁面
