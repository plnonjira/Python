#! /usr/bin/env python
#coding=utf-8
### Func. : Read Database of SURF_CLI_CHN_MUL_DAY_V3.0
### Author: Liangjun Zhu
### Date  : 2016-4-11
### Email : zlj@lreis.ac.cn
### Blog  : zhulj.net

import os,sys,datetime,time
import sqlite3
def get_conn(path):
    '''
    get connection of Sqlite
    :param path: path of Sqlite database
    '''
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        #print('database in hardware :[{}]'.format(path))
        return conn
    else:
        conn = None
        #print('database in memory :[:memory:]')
        return sqlite3.connect(':memory:')
def get_cursor(conn):
    '''
    get cursor of current connection
    :param conn: connection of Sqlite
    '''
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()
def close_all(conn, cu):
    '''
    close connection and cursor of Sqlite
    :param conn: connection of Sqlite
    :param cu: cursor of conn
    '''
    try:
        if cu is not None:
            cu.close()
    finally:
        if cu is not None:
            cu.close()
def getTablesList(dbpath):
    '''
    Get all tables' name in Sqlite database
    :param dbpath:
    :return: table names
    '''
    conn = sqlite3.connect(dbpath)
    cu = get_cursor(conn)
    tabs = cu.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
    tabList = []
    for tab in tabs:
        tabList.append(tab[0])
    close_all(conn, cu)
    return tabList
def fetchData(conn, sql):
    '''
    Query data by sql
    :param conn:
    :param sql:
    :return: data queried
    '''
    data = []
    if sql is not None and sql != '':
        cu = get_cursor(conn)
        cu.execute(sql)
        r = cu.fetchall()
        if len(r) > 0:
            for e in range(len(r)):
                #print r[e]
                data.append(r[e])
    else:
        print('the [{}] is empty or equal None!'.format(sql))
    return data
def saveToCSV(data, csvPath, flag='climData'):
    f = open(csvPath, "w")
    title = ''
    if flag == 'climData':
        title = 'stationID,date,avgTEM,maxTEM,minTEM,avgRHU,minRHU,PRE208,PRE820,PRE,smEVP,lgEVP,avgWIN,maxWIN,maxWINASP,extWIN,extWINASP,SSD\n'
    elif flag == 'stationInfo':
        title = 'stationID,lat,lon,alti\n'
    f.write(title)
    for items in data:
        itemsStr = ''
        if flag == 'stationInfo':
            items = items[0]
        for item in items:
            itemsStr += str(item)
            itemsStr += ','
        itemsStr = itemsStr[:-1]
        itemsStr += '\n'
        f.write(itemsStr)
    f.close()
def QueryDatabase(dbpath, savePath, stationIDs, startTime, endTime):
    '''
    Query and save data from Sqlite database
    :param dbpath:
    :param savePath:
    :param stationIDs:
    :param startTime:
    :param endTime:
    :return:
    '''
    tableList = getTablesList(dbpath)
    conn = sqlite3.connect(dbpath)
    stationInfoCSVPath = savePath + os.sep + 'stationInfo.csv'
    stationInfoData = []
    for stationID in stationIDs:
        tabName = 'S' + stationID
        if tabName in tableList:
            csvPath = savePath + os.sep + tabName + '.csv'
            startT = datetime.datetime(startTime[0], startTime[1], startTime[2])
            endT = datetime.datetime(endTime[0], endTime[1], endTime[2])
            startTStr = startT.strftime("%Y-%m-%d %H:%M:%S")[:10]
            endTStr = endT.strftime("%Y-%m-%d %H:%M:%S")[:10]
            fetch_data_sql = '''SELECT * FROM %s WHERE date BETWEEN "%s" AND "%s" ORDER BY date''' % (tabName, startTStr, endTStr)
            #print fetch_data_sql
            data = fetchData(conn,fetch_data_sql)
            saveToCSV(data, csvPath)
            fetch_station_sql = '''SELECT * FROM stationInfo WHERE stID=%s ''' % (stationID)
            stationInfoData.append(fetchData(conn,fetch_station_sql))
    saveToCSV(stationInfoData, stationInfoCSVPath,'stationInfo')
    conn.close()


if __name__ == '__main__':
    ## Input parameters
    SQLITE_DB_PATH = r'E:\data\common_GIS_Data\SURF_CLI_CHN_MUL_DAY_V3.0\test3.db'
    QUERY_STATION_IDs = ['53845', '53754']
    QUERY_DATE_FROM = [1951,1,1] ## format: Year, Month, Day
    QUERY_DATE_END  = [2016,1,1]
    SAVE_PATH = r'E:\data\common_GIS_Data\SURF_CLI_CHN_MUL_DAY_V3.0'

    QueryDatabase(SQLITE_DB_PATH, SAVE_PATH, QUERY_STATION_IDs, QUERY_DATE_FROM, QUERY_DATE_END)