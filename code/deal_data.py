# -*- coding: utf-8 -*-

import math, csv, datetime, time, glob, os, json ,re
from geopy.distance import vincenty
import pandas as pd

EARTH_REDIUS = 6378.137

def getTimeDiff(timeStra,timeStrb):
    "用来求时差(秒)"
    if timeStra>=timeStrb:
        raise Exception("时间先后出错")
    ta = time.strptime(timeStra, "%Y-%m-%d %H:%M:%S")
    tb = time.strptime(timeStrb, "%Y-%m-%d %H:%M:%S")
    y,m,d,H,M,S = ta[0:6]
    dataTimea = datetime.datetime(y,m,d,H,M,S)
    y,m,d,H,M,S = tb[0:6]
    dataTimeb = datetime.datetime(y,m,d,H,M,S)
    secondsDiff = (dataTimeb-dataTimea).total_seconds()
    return secondsDiff

def getDayDiff(timeStra,timeStrb):
    """
    用来求以天为单位的时差
    用在判断是否要更新省市县信息和求天气时用
    所以只要日期在下一天，就认为隔了一天，不考虑要达到24小时
    """
    ta = time.strptime(timeStra, "%Y-%m-%d %H:%M:%S")
    tb = time.strptime(timeStrb, "%Y-%m-%d %H:%M:%S")
    y,m,d,H,M,S = ta[0:6]
    dataTimea = datetime.datetime(y,m,d)
    y,m,d,H,M,S = tb[0:6]
    dataTimeb = datetime.datetime(y,m,d)
    daysDiff = abs((dataTimeb-dataTimea).days)
    return daysDiff

def getRad(angle):
    "转换成弧度制"
    return angle * math.pi / 180.0

def getMSSpeed(speed):
    "速度换算成米每秒"
    return speed / 3.6

def getNewLngandLat(lng0, lat0, angle, speed, deltatime):
    "求下一点的经纬度"
    one_meter_to_Lng = 1.0 / (vincenty((lat0, lng0), (lat0, lng0 + 0.01)).meters * 100) #每一米对应当前多少经度
    one_meter_to_Lat = 1.0 / (vincenty((lat0, lng0), (lat0 + 0.01, lng0)).meters * 100) #每一米对应当前多少纬度
    rad_angle = getRad(angle) #换算成弧度角
    ms_speed = getMSSpeed(speed) #换算成米每秒速度
    delta_distance = ms_speed * deltatime #求距离(单位：米)
    #根据角度的四个区间采用不同的公式进行运算
    if rad_angle >= 0 and rad_angle < math.pi / 2:
        lng1 = lng0 + (delta_distance * math.sin(rad_angle)) * one_meter_to_Lng
        lat1 = lat0 + (delta_distance * math.cos(rad_angle)) * one_meter_to_Lat
    elif rad_angle >= math.pi / 2 and rad_angle < math.pi:
        lng1 = lng0 + (delta_distance * math.cos(rad_angle - math.pi / 2)) * one_meter_to_Lng
        lat1 = lat0 - (delta_distance * math.sin(rad_angle - math.pi / 2)) * one_meter_to_Lat
    elif rad_angle >= math.pi and rad_angle < math.pi * 3 / 2:
        lng1 = lng0 - (delta_distance * math.sin(rad_angle - math.pi)) * one_meter_to_Lng
        lat1 = lat0 - (delta_distance * math.cos(rad_angle - math.pi)) * one_meter_to_Lat
    else:
        lng1 = lng0 - (delta_distance * math.cos(rad_angle - math.pi * 3 / 2)) * one_meter_to_Lng
        lat1 = lat0 + (delta_distance * math.sin(rad_angle - math.pi * 3 / 2)) * one_meter_to_Lat

    return lng1, lat1

def getPreSpeed(lng0, lat0, lng1, lat1, deltatime):
    "这是用来计算速度的"
    length = vincenty((lat0, lng0), (lat1, lng1)).kilometers #换算成公里制距离
    deltatime = deltatime / (60 * 60) #换算成小时制
    return length / deltatime #返回(lng0,lat0)点时的速度

def getLocation(jsondictlist, lng, lat):
    "利用地理位置json文件来对经纬度求最近的地理位置"
    mindistance = vincenty((float(jsondictlist[0]['latitude']), float(jsondictlist[0]['longitude'])), (lat, lng)).meters
    mindistancedict = jsondictlist[0] #储存与lng,lat距离最短的dict
    for dictx in jsondictlist:
        if (vincenty((float(dictx['latitude']), float(dictx['longitude'])), (lat, lng)).meters < mindistance):
            mindistance = vincenty((float(dictx['latitude']), float(dictx['longitude'])), (lat, lng)).meters
            mindistancedict = dictx #更新距离最短的dict

    return mindistancedict['province'], mindistancedict['city'], mindistancedict['county']

def getWeather(weatherlist, date_time, province, city, county):
    "求指定省市县指定日期时间的天气情况"
    for weather in weatherlist:
        if getDayDiff((weather[10].split('/')[2]+'-'+weather[10].split('/')[1]+'-'+weather[10].split('/')[0]+' 00:00:00').replace('/', '-'), date_time) == 0 \
                and weather[1] in city and weather[0] in province:
            return weather[3:-1] #时间和地理位置一致则传回天气信息
    return ['','','','','','',''] #天气不存在则传回空值

def deleteDuplicates(file):
    "利用pandas进行去重"
    df = pd.read_csv(file, header = 0, low_memory=False)
    dataframe = df.drop_duplicates()
    dataframe.to_csv(file, encoding="utf_8_sig", index = 0)

def dealAndCreateFile(file, time_threshold, length_threshold, jsondictlist, weatherlist, speed_threshold):
    """
    这个函数用来对一个csv表进行数据预处理：
    1.去除重复数据
    2.对偏移数据进行修正
    3.对异常数据进行删除
    4.将每一段的路程之间用一行标识数据（lng为0）隔开，便于前端的展示
    5.为每一条数据添加省市县信息
    6.为每一条数据添加天气信息
    7.去除重复数据
    最后将处理后的数据作为一个新csv表存储起来
    """
    deleteDuplicates(file)  # 调用去重函数
    filepath, tmpfilename = os.path.split(file)
    shotname, extension = os.path.splitext(tmpfilename)
    with open(file, encoding = "utf-8") as f:
        reader = csv.reader(f)
        reader = list(reader)
        listdata = [reader[0], reader[1]] #新建的list作为处理后数据的容器，最终将存进新的csv作为处理后的表
        listdata[0].extend(['province', 'prefecture_city', 'county', 'wind_direction', 'wind_power', 'high_temp', 'low_temp', 'conditions', 'relative_humidity', 'precipitation'])  # 增加省市县的数据项
        listdata[1].extend(list(getLocation(jsondictlist, listdata[1][3], listdata[1][4]))) #对第一条数据添加省市县信息
        listdata[1].extend(list(getWeather(weatherlist, listdata[1][10], listdata[1][13], listdata[1][14], listdata[1][15]))) #对第一条数据添加天气信息
        updatedlocation = listdata[1]

        for row in reader[2:]:  # 从第三行开始判断处理
            lastrowinnewdata = listdata[-1]  #新表的最后一条数据，用于计算当前处理的数据的行数
            #时间一致或时间小于3秒里程数却变化超过1公里则跳过
            if (listdata[-1][10] == row[10]) or (getTimeDiff(listdata[-1][10], row[10]) < 3 and int(row[12])-int(listdata[-1][12]) >= 1):
                continue

            # 如果速度超过阈值，按漂移数据进行处理
            if vincenty((listdata[-1][4], listdata[-1][3]), (row[4], row[3])).meters/getTimeDiff(listdata[-1][10], row[10]) > speed_threshold:
                print('该条数据发生了可处理的长距离偏移,是原表的第{}行，处理后是新表的第{}行'.format(reader.index(row) + 1, \
                            listdata.index(lastrowinnewdata) + 2))  # 打印大致的行号，便于检查出错点
                deltatime = getTimeDiff(listdata[-1][10], row[10])
                if deltatime > 3: #两条数据间隔时间超过三秒，则可认定因堵车或红路灯等原因引起的特殊情况，求下一经纬的间隔时间按照1s计算
                    deltatime = 1
                lng1, lat1 = (getNewLngandLat(float(listdata[-1][3]), float(listdata[-1][4]), int(listdata[-1][2]), float(listdata[-1][11]), deltatime)) # 计算新的经纬坐标
                row[3] = lng1
                row[4] = lat1  # 用新的经纬进行修正

            # 如果速度为零且时间超过阈值且距离变化超过阈值，则认为是脏数据，不添加到新的csv
            elif(float(row[11]) == 0 and getTimeDiff(listdata[-1][10], row[10]) >= time_threshold \
                    and vincenty((listdata[-1][4], listdata[-1][3]), (row[4], row[3])).kilometers > length_threshold):
                print("该条数据是原表的{}行，数据异常，不添加进新表".format(reader.index(row) + 1))
                continue

            else:
                print('该条数据没有发生长距离偏移，是原表的第{}行，是新表的第{}行'.format(reader.index(row) + 1, \
                    listdata.index(lastrowinnewdata) + 2))  # 打印大致的行号，便于检查出错点

            appendlisttemp = row  # 用来添加省市县和天气而设置的临时列表
            #如果和上一次更新省市县信息时的位置相隔超过5千米或者日期不同，则重新查找省市县和天气情况
            if (vincenty((updatedlocation[4], updatedlocation[3]), (row[4], row[3])).kilometers > 5 or getDayDiff(updatedlocation[10], row[10]) > 0):
                appendlisttemp.extend(list(getLocation(jsondictlist, row[3], row[4])))  # 增加省市县
                appendlisttemp.extend(list(getWeather(weatherlist, row[10], row[13], row[14], row[15]))) #增加天气
                updatedlocation = appendlisttemp
            else:#否则和上条数据一致（这么做是为了提高程序运行速度）
                appendlisttemp.extend(listdata[-1][13:])

            # 如果时间大于等于阈值且距离变化超过阈值，则当做一段路程的结束，加入一行标识数据（lng和lat为0，其他和原表的上一条数据一样）
            if ((getTimeDiff(listdata[-1][10], row[10]) >= time_threshold \
                    and vincenty((listdata[-1][4], listdata[-1][3]), (row[4], row[3])).kilometers > length_threshold)) \
                    or getTimeDiff(listdata[-1][10], row[10]) >= 10*60:
                tupletemp = listdata[-1]  # 用来添加 标识行 数据的临时元祖
                listtemp = list(tupletemp)  # 用来添加 标识行 数据的临时列表
                listtemp[3] = 0
                listtemp[4] = 0
                listdata.append(listtemp)

            listdata.append(appendlisttemp) #添加至储存新数据的容器中
            lastrowinnewdata = appendlisttemp #更新最后一条数据

        # 最后一行也要加上lng以及lat为零的标识符，统一格式
        tupletemp = listdata[-1]  # 用来添加 标识行 数据的临时元祖
        listtemp = list(tupletemp)  # 用来添加 标识行 数据的临时列表
        listtemp[3] = 0
        listtemp[4] = 0
        listdata.append(listtemp)
            # 加上dealed作为处理后的数据文件名
        with open(filepath + '\\' + shotname + 'dealed' + extension, 'w', encoding='utf-8', newline='') as fw:
            writer = csv.writer(fw)
            writer.writerows(listdata)
        deleteDuplicates(filepath + '\\' + shotname + 'dealed' + extension) #调用去重函数

def dealWeather(weather_reader):
    '''
    将天气格式化
    '''
    weatherlist = weather_reader[1:]  # 用一个新的list进行存储
    for weather in weatherlist:  # 将风向转为角度

        if weather[3] == '北风':
            weather[3] = str(0)
        elif weather[3] == '东北风':
            weather[3] = str(45)
        elif weather[3] == '东风':
            weather[3] = str(90)
        elif weather[3] == '东南风':
            weather[3] = str(135)
        elif weather[3] == '南风':
            weather[3] = str(180)
        elif weather[3] == '西南风':
            weather[3] = str(225)
        elif weather[3] == '西风':
            weather[3] = str(270)
        elif weather[3] == '西北风':
            weather[3] = str(315)
        else:
            weather[3] = str(-1)  # -1代表无持续风向或数据缺失

        windpower_list = re.findall(r"\d+\.?\d*", weather[4])
        if(len(windpower_list) != 0):
            windpower_list.sort(key=int)
            windpower_list.reverse()
            weather[4] = windpower_list[0]
        else:  #数据缺失则为零
            weather[4] = 0

        weather[5] = weather[5].replace('℃', '')
        weather[6] = weather[6].replace('℃', '')

        if "暴雪" in weather[7]:
            weather[7] = "暴雪"
        elif "暴雨" in weather[7]:
            weather[7] = "暴雨"
        elif "大雪" in weather[7]:
            weather[7] = "大雪"
        elif "大雨" in weather[7]:
            weather[7] = "大雨"
        elif "中雪" in weather[7]:
            weather[7] = "中雪"
        elif "中雨" in weather[7]:
            weather[7] = "中雨"
        elif "小雪" in weather[7]:
            weather[7] = "小雪"
        elif "小雨" in weather[7]:
            weather[7] = "小雨"
        elif "阵雨" in weather[7]:
            weather[7] = "阵雨"

    return weatherlist

if __name__ == '__main__':
    #针对个别数据表可能需要修改阈值
    time_threshold = 200 #时间阈值
    length_threshold = time_threshold * 200 / (2 * 60 * 60) #距离阈值
    speed_threshold = 42 # 速度阈值

    with open("china_places.json", 'r') as load_f:
        load_dict = json.load(load_f)
        jsondictlist = [] #加载json后，用一个新的list进行存储
        for dictx in load_dict[1:]:
            # if (dictx['city'] != dictx['county']): #去掉json中的首行 以及 市和县相同的数据行
            jsondictlist.append(dictx)

    with open("weather.csv", 'r') as weather_f:
        weather_reader = csv.reader(weather_f)
        weather_reader = list(weather_reader)
        weatherlist = dealWeather(weather_reader)

    filelist = glob.glob(r'D:\BDMR\testdata\*csv')
    for file in filelist: #循环读取待处理文件
        print("正在处理第{}个文件".format(filelist.index(file) + 1))
        dealAndCreateFile(file, time_threshold, length_threshold, jsondictlist, weatherlist) #调用处理函数对数据进行处理并生成新的csv文件存储处理后的数据

    #测试
    # file = r'D:\BDMR\10tables\originaldata\AD00003.csv'
    # dealAndCreateFile(file, time_threshold, length_threshold, jsondictlist, weatherlist, speed_threshold)
