from mysqlmethods import mysql

# Reset tables if exist
mysql.tableDBControl(
    """DROP TABLE IF EXISTS stationinfo,
stopofstation,
operator,
busroute,
operatorofroute,
stopofroute"""
)

# Create tables
mysql.tableDBControl(
    """CREATE TABLE stationinfo(
stationUID VARCHAR(16) PRIMARY KEY,
stopname_tw VARCHAR(32),
stopname_en VARCHAR(128),
address VARCHAR(64),
coordinate POINT NOT NULL SRID 3826,
SPATIAL INDEX(coordinate))"""
)
mysql.tableDBControl(
    """CREATE TABLE stopofstation(
stopUID VARCHAR(16) PRIMARY KEY,
stationUID VARCHAR(16),
FOREIGN KEY (stationUID)
REFERENCES stationinfo(stationUID) ON UPDATE CASCADE ON DELETE SET NULL)"""
)
mysql.tableDBControl(
    """CREATE TABLE operator(
operatorID VARCHAR(8) PRIMARY KEY,
oname_tw VARCHAR(8),
oname_en VARCHAR(32),
phone VARCHAR(16),
webpage VARCHAR(64))"""
)
mysql.tableDBControl(
    """CREATE TABLE busroute(
routeUID VARCHAR(16) PRIMARY KEY,
routename_tw VARCHAR(16),
routename_en VARCHAR(64),
linestrings GEOMETRY,
depname_tw VARCHAR(16),
depname_en VARCHAR(64),
destname_tw VARCHAR(16),
destname_en VARCHAR(64),
routeimgurl TEXT,
UNIQUE INDEX(routename_tw))"""
)
mysql.tableDBControl(
    """CREATE TABLE operatorofroute(
ofrID SMALLINT AUTO_INCREMENT PRIMARY KEY,
routeUID VARCHAR(16),
operatorID VARCHAR(16),
FOREIGN KEY (routeUID)
REFERENCES busroute(routeUID) ON UPDATE CASCADE ON DELETE SET NULL,
FOREIGN KEY (operatorID)
REFERENCES operator(operatorID) ON UPDATE CASCADE ON DELETE SET NULL)"""
)
mysql.tableDBControl(
    """CREATE TABLE stopofroute(
srID MEDIUMINT AUTO_INCREMENT PRIMARY KEY,
routeUID VARCHAR(16),
direction TINYINT,
stopUID VARCHAR(16),
stopsequence TINYINT,
FOREIGN KEY (routeUID)
REFERENCES busroute(routeUID) ON UPDATE CASCADE ON DELETE SET NULL,
FOREIGN KEY (stopUID)
REFERENCES stopofstation(stopUID) ON UPDATE CASCADE ON DELETE SET NULL)"""
)
