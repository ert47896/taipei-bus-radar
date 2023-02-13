# [Taipei Bus Radar](https://bus.taipeilife.site/) 台北市公車動態資訊網站

This website is built with realtime Taipei City bus data from [Transport Data wXchange](https://tdx.transportdata.tw/).
Features include:
* Show realtime bus locations and operation information (include speed, platenumber, route number, route origin and destination and estimated time of arrival)
* Show the pass by routes for selected bus station
* Show the bus stations informantion according the address which user inputed


## Demo
Taipei Bus Radar website：https://bus.taipeilife.site/<br>

## Skills
* Created with Python Flask
* Combined Nginx, Flask, MySQL and Let's Encrypt(auto renew SSL certification) with Docker Compose for rapid deployment
* Applied GitHub Actions for CI/CD
* Used MySQL and Flask-caching for storing data
* Designed MySQL database in Third Normal Form
* Applied Index and Foreign key in MySQL database
* Built RESTful style API
* Used Jinja2 to build template
* Set up the web map via Leaflet
* Used Google Geocoding API for decoding address to latitude and longitude
* Deployed website on AWS EC2

## System Architecture Diagrame
![bus-architecture](https://user-images.githubusercontent.com/24973056/218423045-25de1c77-8e4d-44fa-b5f5-a960608c6e3a.png)

## MySQL Database Schema
![MySQL Schema](https://user-images.githubusercontent.com/24973056/128684156-398f38ac-8a9b-481c-afab-85fcabc10225.png)


## Features
### Homepage

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
