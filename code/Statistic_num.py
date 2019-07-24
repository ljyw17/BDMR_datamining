# -*- coding: utf-8 -*-

'''
统计每一辆车的安全、效率、能耗情况。
安全：疲劳驾驶、急加速、急减速、怠速预热、 超长怠速、熄火滑行、超速、急变道、安全行驶里程之外、速度稳定性低、低能见度时超出限速、
      侧风高速行驶、八级及以上风时驾驶、不良天气驾驶速度过高。
效率：汽车运行时的平均速度
能耗：行急加速、急减速、车速稳定性、怠速过长、逆风高速、非经济车速比例
'''

import pandas as pd
import datetime, numpy, math, glob, io, sys, os, csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编


rapid_times = 0  # 急加速次数
deceleration_times = 0  # 急减速册数
fatigueDriving_times = 0  # 疲劳驾驶次数
idlePreheating_times = 0  # 怠速预热次数
overlongIdle_times = 0  # 超长怠速次数
coastingEngineoff_times = 0  # 熄火滑行次数
speeding_times = 0  # 超速次数
changeRoad_times = 0  # 急变道次数

safeMiles_flag = 0  # 是否在安全行驶里程范围内，0代表安全，1代表超出安全行驶里程
average_speed = 0  # 汽车运行时的平均速度
speed_stabilization = 0  # 行驶时的速度稳定性
lowVisibilitySpeeding_times = 0  # 低能见度时超出限速次数
crossWind_time = 0  # 侧风高速行驶的时长
highWind_time = 0  # 八级及以上风时驾驶时长
adverseweatherSpeeding_times = 0  #  不良天气驾驶速度过高次数
againstWind_time = 0  # 逆风时高速驾驶时长
diseconomicSpeed_rate = 0  # 非经济车速比率


def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    return data

def split_time(time):
    time = time.split(' ')
    pre = time[0].split('-')
    las = time[1].split(':')
    year = pre[0]
    month = pre[1]
    day = pre[2]
    hour = las[0]
    minutes = las[1]
    second = las[2]
    return year, month, day, hour, minutes, second

def Timeline(time1, time2):
    t1_year, t1_month, t1_day, t1_hour, t1_min, t1_sec = split_time(time1)
    t2_year, t2_month, t2_day, t2_hour, t2_min, t2_sec = split_time(time2)
    d1 = datetime.datetime(int(t1_year), int(t1_month), int(t1_day), int(t1_hour), int(t1_min), int(t1_sec))
    d2 = datetime.datetime(int(t2_year), int(t2_month), int(t2_day), int(t2_hour), int(t2_min), int(t2_sec))
    sec = (d2 - d1).total_seconds()
    # print(sec)
    return sec

def find_rapid_decelerate(data):
    '''
    统计急加速，急减速的次数
    '''
    global rapid_times, deceleration_times
    speed = data['gps_speed']
    time = data['location_time']
    lng = data['lng']
    for i in range(len(data) - 1):
        sec = Timeline(time[i], time[i + 1])
        a = speed[i + 1] - speed[i]
        # print(a)
        # print(sec)
        if lng[i] != 0:
            if sec == 1:
                if a > 10.8:
                    rapid_times += 1
                    # print(lng[i], lng[i + 1])
                elif a < -10.8:
                    # print(time[i])
                    deceleration_times += 1
            elif sec == 2:
                if a > 21.6:
                    rapid_times += 1
                elif a < -21.6:
                    deceleration_times += 1
            elif sec == 3:
                if a > 32.4:
                    rapid_times += 1
                elif a < -32.4:
                    deceleration_times += 1

def find_idlePreheating(data):
    '''
    统计怠速的时间
    '''
    acc_state = data['acc_state']
    time = data['location_time']
    speed = data['gps_speed']
    mile = data['mileage']
    change = True  # 这个标记用来统计车辆的当天首次启动
    acc_change = True  # 这个标记当acc状态熄火时，在返回的列表中添加0当标志位，用来分隔怠速预热和超长怠速
    times = []  # 每次往列表中添加时间，用来每次将最后一个和第一个时间进行时间间隔的计算，返回秒数
    daisu_times = []  # 函数返回的列表，每个元素是每次怠速的时间统计，即acc_state=1且speed为0的时间，怠速预热和超长怠速
    for i in range(len(data) - 1):
        if mile[i + 1] - mile[i] < 2:  # 数据中出现的跳跃数据，下条数据的里程比上条数据的里程多太多
            if acc_state[i] == 1:
                acc_change = True
                if speed[i] == 0 and change:
                    times.append(time[i])
                    change = False
                elif speed[i] == 0:
                    times.append(time[i])
                    if i == len(data) - 2:
                        # print(times[0], times[-1])
                        timeline = Timeline(times[0], times[-1])
                        daisu_times.append(timeline)
                        # print(timeline)
                        times.clear()
                elif speed[i] != 0:
                    if len(times) <= 2:
                        times.clear()
                    else:
                        # print(times[0], times[-1])
                        timeline = Timeline(times[0], times[-1])
                        # print(timeline)
                        daisu_times.append(timeline)
                        times.clear()
            elif acc_state[i] == 0:
                if len(times) > 2:
                    # print(times[0], times[-1])
                    timeline = Timeline(times[0], times[-1])
                    # print(timeline)
                    daisu_times.append(timeline)
                    times.clear()
                if acc_change:
                    # print('熄火了')
                    daisu_times.append(0)
                    acc_change = False
        else:
            if len(times) > 2:
                # print(times[0], times[-1])
                timeline = Timeline(times[0], times[-1])
                # print(timeline)
                daisu_times.append(timeline)
                times.clear()
    return daisu_times

def find_idlePreheatingandOver(data):
    '''
    计算怠速预热和超长怠速次数
    怠速预热判断依据：怠速预热为车辆从发动机启动到车辆起步的过程，要求：
    （1）车辆的速度为0（2）acc=1 (3)acc=1为当天首次启动或者该数据的上一条acc=0
    '''
    global idlePreheating_times, overlongIdle_times
    daisu_times = find_idlePreheating(data)
    # print(len(daisu_times))
    # print(daisu_times)
    index_yure = []
    for i in range(len(daisu_times)):
        if daisu_times[i] == 0 and daisu_times[-1] != 0:
            index_yure.append(daisu_times[i + 1])
            daisu_times[i + 1] = 1
    # print(daisu_times)
    # print(index_yure)
    for i in daisu_times[1:]:
        if i > 120:
            overlongIdle_times += 1
    for i in index_yure:
        if i > 120:
            idlePreheating_times += 1
    if daisu_times[0] > 120:
        idlePreheating_times += 1

def find_fatigueDriving(data):
    '''
    统计疲劳驾驶的次数
    疲劳驾驶判别依据：24小时内驾驶时间>=8小时or（连续驾驶时间>=4小时and休息时间<=20分钟）
    '''
    traffic_light_threshold = 4 * 60  # 等红绿灯的时间阈值

    global fatigueDriving_times  # 疲劳驾驶次数
    speeds = data['gps_speed']
    times = data['location_time']
    acc = data['acc_state']
    drivetime4 = 0  # 设置这个驾驶时间是为了判断是否满足"连续驾驶时间>=4小时and休息时间<=20分钟"
    drivetime24 = 0  # 设置这个驾驶时间是为了判断是否满足"24小时内驾驶时间>=8小时"
    breaktime = 0  # 设置这个休息时间是为了判断是否满足"连续驾驶时间>=4小时and休息时间<=20分钟"
    flag = 2  # 最先进入flag为2的判断语句块中
    for i in range(len(data) - 1):  # 一条条的读

        if(drivetime4 >= 4 * 60 * 60):  # 始终都在判断驾驶时间是否超过4小时
            if(breaktime < 20 * 60):  # 而且休息时间低于20分钟
                fatigueDriving_times += 1  # 累加一次疲劳驾驶行为
                # print("驾驶时间{},休息时间{}".format(drivetime4, breaktime))
            breaktime = 0  # 初始化休息时间
            drivetime4 = 0  # 初始化 用于判断 "连续驾驶时间>=4小时and休息时间<=20分钟"行为而设的 驾驶时间
            flag = 1  # 初始化后，进到flag为1的语句块中，重新开始判断"连续驾驶时间>=4小时and休息时间<=20分钟"

        if('begintime' in dir() and Timeline(begintime, times[i]) >= 24 * 60 * 60):  # 始终都在判断和最初记录的时间的间隔是否超过24小时
            if(drivetime24 >= 8 * 60 * 60):  # 如果在这24小时里，驾驶时长超过8小时
                fatigueDriving_times += 1  # 累积一次疲劳驾驶行为
                # print(begintime, times[i])
                # print("开始时间{}, 驾驶时间{}".format(Timeline(begintime, times[i]), drivetime24))
            breaktime = 0
            drivetime4 = 0
            drivetime24 = 0  # 初始化三个参数
            flag = 2  # 进到flag为2的语句块中，完全重新开始

        if(flag == 2):  # 最初以及后续初始化的语句块
            if(speeds[i] != 0 and acc[i] != 0 and Timeline(times[i], times[i + 1]) <= 3):  # 如果速度不为零而且间隔时间属于驾驶状态的正常情况
                begintime = times[i]  # 记录开始时间，用于判断时间间隔是否达到24小时
                drivetime4 += Timeline(times[i], times[i + 1])  # 驾驶的这几秒累加到两个驾驶时间量上
                drivetime24 += Timeline(times[i], times[i + 1])
                flag = 1  # 下一次跳到flag为1的判断语句块中
                continue

        if(flag == 1):
            if(speeds[i] != 0 and acc[i] != 0 and Timeline(times[i], times[i + 1]) <= 3):  # 如果速度不为零而且间隔时间属于驾驶状态的正常情况
                drivetime4 += Timeline(times[i], times[i + 1])  # 驾驶的这几秒累加到两个驾驶时间量上
                drivetime24 += Timeline(times[i], times[i + 1])
            elif(speeds[i] == 0 and Timeline(times[i], times[i + 1]) <= 3):  # 如果速度为零且间隔时间属于驾驶状态的正常情况，开始记录持续时间
                zeroduration = Timeline(times[i], times[i + 1])  # 速度为零的持续时间
                flag = 0  # 跳到flag为0的语句块，开始记录速度为零的持续时间
            continue

        if(flag == 0):
            if(speeds[i] == 0 and Timeline(times[i], times[i + 1]) <= 3):  # 速度为零且间隔时间属于驾驶状态的正常情况，则把间隔时间累加到速度为零的持续时间
                zeroduration += Timeline(times[i], times[i + 1])
            else:
                if(zeroduration > traffic_light_threshold):  # 当速度不为零了，开始判断持续时间是否超过阈值，以决定这段时间是在等红灯还是休息
                    breaktime += zeroduration  # 超过阈值则认为是在休息，累加到休息时间中
                else:
                    drivetime4 += zeroduration  # 否则认为是在等交通信号灯，把时间累加到两个记录驾驶时间上
                    drivetime24 += zeroduration
                flag = 1  # 判断完后，下一步执行flag为1的语句块

def find_coastingEngineoff(data):
    '''
    统计熄火滑行的次数
    判单依据：熄火行驶（acc状态 == 0 and gps速度 ！= 0 and 持续时间>=1s）
    '''
    global coastingEngineoff_times
    acc_state = data['acc_state']
    speed = data['gps_speed']
    time = data['location_time']
    times = []
    num = 0
    for i in range(len(data)):
        if acc_state[i] == 0 and speed[i] != 0:
            times.append(time[i])
        else:
            if len(times) >= 2:
                timeline = Timeline(times[0], times[-1])
                # print(times[0], times[-1])
                # print(timeline)
                coastingEngineoff_times += 1
                times.clear()
            elif len(times) == 1:
                # print(times[0])
                coastingEngineoff_times += 1
                times.clear()

def whether_safeMilesRange(data):
    '''
    判断是否超出了安全行驶里程
    安全行驶里程是40 万公里
    '''

    global safeMiles_flag
    if (data.at[len(data) - 2, 'mileage'] > 400000):  # 直接判断数据最后的里程数是否超过40万公里
        safeMiles_flag = 1

def find_overSpeed(data):
    '''
    统计超速的次数
    超速判断依据：GPS速度>=100km/h and 持续时间>=3s
    '''
    overspeed_time_threshold = 3  # 判定超速的时间阈值

    global speeding_times  # 疲劳驾驶次数
    speeds = data['gps_speed']
    times = data['location_time']
    flag = 0
    for i in range(len(data) - 1):

        if('overSpeed_duration' in dir() and overSpeed_duration >= overspeed_time_threshold):  # 判断持续超速的时间是否超过阈值
            speeding_times += 1  # 累计超速次数
            overSpeed_duration = 0  # 持续时间重置
            flag = 0  # 重新开始寻找第一个超速的点

        if(flag == 0 and speeds[i] >= 100 and Timeline(times[i], times[i + 1]) <= 3):  # 第一个超速点
            overSpeed_duration = Timeline(times[i], times[i + 1])  # 记录第一个超速时间间隔
            flag = 1  # flag设置为1，开始计算持续时间
            continue

        if(flag == 1):
            if(speeds[i] >= 100 and Timeline(times[i], times[i + 1]) <= 3):  # 超速
                overSpeed_duration += Timeline(times[i], times[i + 1])  # 累积时间
            else:
                overSpeed_duration = 0  # 没超速则重置，重新开始
                flag = 0

def find_avgSpeedandSta(data):
    '''
    计算出速度的平均值和标准差
    '''
    global average_speed, speed_stabilization
    speeds = data['gps_speed']
    speedlist = []

    [speedlist.append(speeds[i]) for i in range(len(data) - 1) if speeds[i] != 0]  # 把速度非零的值加入到列表中

    narray = numpy.array(speedlist)
    sum1 = narray.sum()  # 求非零速度的总值
    narray2 = narray * narray
    sum2 = narray2.sum()  # 求非零速度的平方和
    if(len(speedlist)):
        average_speed = sum1 / len(speedlist)  # 平均速度
        speedStandard_deviation = math.sqrt(sum2 / len(speedlist) - average_speed ** 2)  # 速度的标准差
        speed_stabilization = 1 - speedStandard_deviation / max(speedlist)  # 根据标准差，计算出稳定性
    else: #速度全为零，则平均速度为零,稳定性为1
        average_speed = 0
        speed_stabilization = 1

def get_diffAngle(angle1, angle2):
    '''
    计算角度差
    '''
    diffangle1 = abs(angle1 - angle2)
    diffangle2 = 360 - diffangle1
    return diffangle1 if diffangle1 < diffangle2 else diffangle2

def find_changeRoad(data):
    '''
    计算急转弯次数
    定义：速度大于20km/h，且在一秒内角度转动大于等于90度
    '''
    global changeRoad_times
    angles = data['direction_angle']
    speeds = data['gps_speed']
    times = data['location_time']
    # flag = 0
    for i in range(len(data) - 2):
        if (get_diffAngle(angles[i + 1], angles[i]) >= 90 and speeds[i] >= 20 and speeds[i+1] >= 20 and Timeline(times[i], times[i + 1]) == 1):  # 只考虑间隔时间为1s的情况
            changeRoad_times += 1

def get_visibility(precipitation):
    '''
    根据降水量求能见度
    '''
    return 13410 * ((precipitation / 24) ** -0.66)

def find_lowVis_overSpeed(data):
    '''
    找出低能见度时超出限速次数
    限速规定：（一）能见度小于200米时，车速不得超过每小时60公里；
              （二）能见度小于100米时，车速不得超过每小时40公里；
              （三）能见度小于50米时，车速不得超过每小时20公里。
    '''
    global lowVisibilitySpeeding_times

    speeds = data['gps_speed']
    lng = data['lng']
    precipitations = data['precipitation']
    for i in range(len(data) - 1):  # 根据限速规定判断
        if(pd.isnull(precipitations[i]) == False and get_visibility(precipitations[i]) < 50 and speeds[i] > 20 and lng[i] != 0):
            lowVisibilitySpeeding_times += 1
        elif(pd.isnull(precipitations[i]) == False and get_visibility(precipitations[i]) < 100 and speeds[i] > 40 and lng[i] != 0):
            lowVisibilitySpeeding_times += 1
        elif (pd.isnull(precipitations[i]) == False and get_visibility(precipitations[i]) < 200 and speeds[i] > 60 and lng[i] != 0):
            lowVisibilitySpeeding_times += 1

def find_crosswindDrivetime(data):
    '''
    计算刮侧边大风时高速驾驶的时长
    定义：风力大于等于6级且风向与汽车行驶方向接近垂直且汽车速度大于等于70km/h
    '''
    global crossWind_time
    drive_directions = data['direction_angle']
    speeds = data['gps_speed']
    lng = data['lng']
    times = data['location_time']
    wind_directions = data['wind_direction']
    wind_powers = data['wind_power']
    for i in range(len(data) - 1):
        if(pd.isnull(wind_directions[i]) == False and pd.isnull(wind_directions[i]) == False and wind_powers[i] >= 6 and 45 <= get_diffAngle(wind_directions[i], drive_directions[i]) <= 135
                and speeds[i] >= 70 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):  # 只累积间隔时间在3s以内的
            crossWind_time += Timeline(times[i], times[i + 1])

def find_highwindDrivetime(data):
    '''
    计算8级及以上大风时驾驶的时长
    '''
    global highWind_time
    speeds = data['gps_speed']
    lng = data['lng']
    times = data['location_time']
    wind_powers = data['wind_power']
    for i in range(len(data) - 1):
        if(pd.isnull(wind_powers[i]) == False and wind_powers[i] >= 8 and speeds[i] >= 0 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):  # 只累积间隔时间在3s以内的
            highWind_time += Timeline(times[i], times[i + 1])

def find_adverseweatherSpeeding(data):
    '''
    计算不良天气的高速驾驶次数
    定义不良天气高速：大暴雪及暴雪天：速度大于30km/h;大雪天：速度大于40km/h;中雪天：速度大于50km/h;
    暴雨天：速度大于50km/h;大雨天：速度大于60km/h;中雨天：速度大于80km/h
    '''
    global adverseweatherSpeeding_times
    speeds = data['gps_speed']
    lng = data['lng']
    times = data['location_time']
    conditions = data['conditions']
    for i in range(len(data) - 1):
        if(pd.isnull(conditions[i]) == False and conditions[i] == '暴雪' and speeds[i] > 30 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):  # 只累积间隔时间在3s以内的
            adverseweatherSpeeding_times += 1
        elif (pd.isnull(conditions[i]) == False and conditions[i] == '大雪' and speeds[i] > 40 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):
            adverseweatherSpeeding_times += 1
        elif (pd.isnull(conditions[i]) == False and conditions[i] == '中雪' and speeds[i] > 50 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):
            adverseweatherSpeeding_times += 1
        elif (pd.isnull(conditions[i]) == False and conditions[i] == '暴雨' and speeds[i] > 50 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):
            adverseweatherSpeeding_times += 1
        elif (pd.isnull(conditions[i]) == False and conditions[i] == '大雨' and speeds[i] > 60 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):
            adverseweatherSpeeding_times += 1
        elif (pd.isnull(conditions[i]) == False and conditions[i] == '中雨' and speeds[i] > 80 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):
            adverseweatherSpeeding_times += 1

def find_againstwindDrivetime(data):
    '''
    计算刮逆向大风时高速驾驶的时长
    定义：风力大于等于6级且风向与汽车行驶方向接近相反且汽车速度大于等于70km/h
    '''
    global againstWind_time
    drive_directions = data['direction_angle']
    speeds = data['gps_speed']
    lng = data['lng']
    times = data['location_time']
    wind_directions = data['wind_direction']
    wind_powers = data['wind_power']
    for i in range(len(data) - 1):
        if(pd.isnull(wind_directions[i]) == False and pd.isnull(wind_directions[i]) == False and wind_powers[i] >= 6 and get_diffAngle(wind_directions[i], drive_directions[i]) >= 135
                and speeds[i] >= 70 and Timeline(times[i], times[i + 1]) <= 3 and lng[i] != 0):  # 只累积间隔时间在3s以内的
            againstWind_time += Timeline(times[i], times[i + 1])

def find_diseconomicRate(data):
    '''
    定义：速度属于[70,90]为经济车速
    '''
    global diseconomicSpeed_rate
    speeds = data['gps_speed']
    speedlist = []
    economic_speedlist = []

    [speedlist.append(speeds[i]) for i in range(len(data) - 1) if speeds[i] != 0]  # 把速度非零的值加入到列表中
    [economic_speedlist.append(speeds[i]) for i in range(len(speeds) - 1) if 90 >= speeds[i] >= 70]  # 经济车速加入到列表中
    if len(speedlist) != 0:
        diseconomicSpeed_rate = 1 - len(economic_speedlist) / len(speedlist)
    else: #速度全为零，则直接为一
        diseconomicSpeed_rate = 1

if __name__ == '__main__':

    filelist = glob.glob(r'D:\BDMR\testdata\*dealed.csv')
    for file in filelist: #循环读取待处理文件
        print("正在处理{}".format(file))
        filepath, tmpfilename = os.path.split(file)
        if(filelist.index(file) == 0):
            datalist = [['vehicleplatenumber', 'rapid_times', 'deceleration_times', 'fatigueDriving_times', 'idlePreheating_times', 'overlongIdle_times',
                        'coastingEngineoff_times', 'speeding_times', 'changeRoad_times', 'safeMiles_flag', 'speed_stabilization', 'lowVisibilitySpeeding_times',
                         'crossWind_time', 'highWind_time', 'adverseweatherSpeeding_times', 'average_speed', 'againstWind_time', 'diseconomicSpeed_rate']]

        data = load_data(file)

        #初始化全局变量
        rapid_times = 0  # 急加速次数
        deceleration_times = 0  # 急减速册数
        fatigueDriving_times = 0  # 疲劳驾驶次数
        idlePreheating_times = 0  # 怠速预热次数
        overlongIdle_times = 0  # 超长怠速次数
        coastingEngineoff_times = 0  # 熄火滑行次数
        speeding_times = 0  # 超速次数
        changeRoad_times = 0  # 急变道次数
        safeMiles_flag = 0  # 是否在安全行驶里程范围内，0代表安全，1代表超出安全行驶里程
        speed_stabilization = 0  # 行驶时的速度稳定性
        lowVisibilitySpeeding_times = 0  # 低能见度时超出限速次数
        crossWind_time = 0  # 侧风高速行驶的时长
        highWind_time = 0  # 八级及以上风时驾驶时长
        adverseweatherSpeeding_times = 0  #  不良天气驾驶速度过高次数

        average_speed = 0  # 汽车运行时的平均速度
        againstWind_time = 0  # 逆风时高速驾驶时长
        diseconomicSpeed_rate = 0  # 非经济车速比率

        # 急减速，急加速次数
        find_rapid_decelerate(data)
        print('急加速的次数：', rapid_times)
        print('急减速的次数:', deceleration_times)

        # 疲劳驾驶的次数
        find_fatigueDriving(data)
        print('疲劳驾驶的次数：', fatigueDriving_times)

        find_idlePreheatingandOver(data)
        print('怠速预热的次数：', idlePreheating_times)
        print('超长怠速的次数：', overlongIdle_times)

        # 熄火滑行的次数
        find_coastingEngineoff(data)
        print('熄火滑行的次数：', coastingEngineoff_times)

        # 超速次数
        find_overSpeed(data)
        print('汽车超速次数:', speeding_times)

        # 统计急转弯次数
        find_changeRoad(data)
        print('急转弯次数：', changeRoad_times)

        # 汽车行驶里程是否在安全范围内
        whether_safeMilesRange(data)
        print('汽车行驶里程是否在安全里程内：', safeMiles_flag)

        # 统计平均车速
        find_avgSpeedandSta(data)
        print('速度的稳定性：', speed_stabilization)

        # 低能见度驾驶速度过高次数
        find_lowVis_overSpeed(data)
        print('低能见度驾驶速度过高次数：', lowVisibilitySpeeding_times)

        # 统计测风高速驾驶时长
        find_crosswindDrivetime(data)
        print('侧风高速驾驶时长：', crossWind_time)

        # 统计大风时驾驶时长
        find_highwindDrivetime(data)
        print('八级及以上风级时驾驶时长：', highWind_time)

        #  统计不良天气时驾驶速度过高次数
        find_adverseweatherSpeeding(data)
        print('不良天气驾驶速度过高次数：', adverseweatherSpeeding_times)

        # 打印平均速度
        print('驾驶平均速度：', average_speed)

        # 逆风高速时长
        find_againstwindDrivetime(data)
        print('逆风高速时长', againstWind_time)

        #非经济车数比率
        find_diseconomicRate(data)
        print('非经济车速比例：', diseconomicSpeed_rate)


        datalist.append([data['vehicleplatenumber'][0], rapid_times, deceleration_times, fatigueDriving_times, idlePreheating_times,
                        overlongIdle_times, coastingEngineoff_times, speeding_times, changeRoad_times, safeMiles_flag, speed_stabilization,
                         lowVisibilitySpeeding_times, crossWind_time, highWind_time, adverseweatherSpeeding_times, average_speed, againstWind_time,
                         diseconomicSpeed_rate])

    #写入汇总文件
    with open(filepath + '\\Gatherfile.csv' , 'a', encoding='utf-8', newline='') as fw:
        writer = csv.writer(fw)
        writer.writerows(datalist)
    print('汇总表生成成功')