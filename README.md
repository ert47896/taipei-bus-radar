# [Taipei Bus Radar](https://bus.taipeilife.site/) 台北市公車動態資訊網站

This website is built with real-time Taipei City bus data from [Transport Data wXchange](https://tdx.transportdata.tw/).
Features include:
* Show real-time buses location and operation information(include speed, platenumber, route number, route origin and destination and estimated time of arrival)
* Show the pass by routes for selected bus station
* Show the bus stations informantion according the address which user inputed


## Demo
Taipei Bus Radar website：https://bus.taipeilife.site/<br>

## Skills
* Created with Python Flask, Jinja2
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
![bus-architecture](https://user-images.githubusercontent.com/24973056/218912364-5171f6c6-ddf5-4a50-8033-d05273eda7a2.png)

## MySQL Database Schema
![MySQL Schema](https://user-images.githubusercontent.com/24973056/128684156-398f38ac-8a9b-481c-afab-85fcabc10225.png)


## Features
### Homepage

![image](https://user-images.githubusercontent.com/24973056/128689061-ce8041c6-32d0-40c8-a7d0-49b535c60c9e.png)

1. Click the button then move to user's location on map(need to turn on location permission)
2. Click the bus icon to show operation information
![click bus icon](https://user-images.githubusercontent.com/24973056/218915303-11992a71-829e-4456-bb11-7f11b3486aaf.png)

3. Click the station icon to show estimated time of arrival of that bus stop
![click station](https://user-images.githubusercontent.com/24973056/218915653-c0952eec-a488-4d38-8323-efd9c54d8a2a.png)

![homepage2](https://user-images.githubusercontent.com/24973056/218923794-e05e9427-f0ee-4c25-a5f0-0bb879efa093.png)
4. Search by bus route<br>
5. Search by bus stop

### Route Information Page

![image](https://user-images.githubusercontent.com/24973056/128700003-0ee92499-1bc1-40e5-92aa-789d02dbd991.png)

1. Click the route number to show entire service stops
2. Click the operator name to redirect to official website
3. Press the button to switch route origin and destination for operation information
![origin](https://user-images.githubusercontent.com/24973056/218919837-f72e440d-aacb-42f3-8bf3-ced588baa91f.png)
![destination](https://user-images.githubusercontent.com/24973056/218920013-fba76ba0-13f0-4a6e-960e-00feb09f4ef7.png)

4. Press the stop name to move to the location on map
![press stop name](https://user-images.githubusercontent.com/24973056/218920268-339df0c0-4bb4-43a4-b801-c2bee88f0102.png)

### Search by Bus Stop Page

![search by stop](https://user-images.githubusercontent.com/24973056/128719194-aaff5476-c452-4a99-8d9f-3bd927a1adb7.png)

#### Method A
1. User can click any place on map, then press "Start Search" button
![click any place](https://user-images.githubusercontent.com/24973056/218925050-dd23c9cc-6697-4fe0-abcf-0bbf40642065.png)

2. Get all the bus stops within about three hundreds from that point, choose stop name for detail information
![distance300](https://user-images.githubusercontent.com/24973056/218938213-bb6ae88d-a39f-4c74-848b-23a41461a5a6.png)

#### Method B
Show the bus stations information according the address which user inputted.

### Page of each bus stop

![each bus stop](https://user-images.githubusercontent.com/24973056/128720468-0d6a8d6e-7ecf-4d9c-aa8b-3952a5c1cc37.png)

1. Click to present each route status
2. Show the stop name on map
