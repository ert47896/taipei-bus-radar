from math import sin, cos, sqrt, atan2, radians

R = 6370

# 以經緯度差計算距離-半正矢公式(Haversine formula)
# calDistance([lon1, lat1], [lon2, lat2]) return數值單位為公里
def calDistance(preLocation, nowLocation):
    lon1 = radians(preLocation[0])
    lat1 = radians(preLocation[1])
    lon2 = radians(nowLocation[0])
    lat2 = radians(nowLocation[1])
    diffLon = lon2 - lon1
    diffLat = lat2 - lat1
    a = sin(diffLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(diffLon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance
