# -*- coding: utf-8 -*-

import pandas as pd
import os, csv

if __name__ == "__main__":
    file = r'D:\BDMR\seperate\1trainset.csv'
    filepath, tmpfilename = os.path.split(file)
    data = pd.read_csv(file, low_memory=False)
    firstrowList = ['vehicleplatenumber', 'rapid_times', 'deceleration_times', 'fatigueDriving_times', 'idlePreheating_times', 'overlongIdle_times',
         'coastingEngineoff_times', 'speeding_times', 'changeRoad_times', 'safeMiles_flag', 'speed_stabilization', 'lowVisibilitySpeeding_times',
         'crossWind_time', 'highWind_time', 'adverseweatherSpeeding_times', 'average_speed', 'againstWind_time', 'diseconomicSpeed_rate']
    trainsetList = []
    trainsetList.append(firstrowList) # 训练集列表
    testsetList = []
    testsetList.append(firstrowList) # 测试集列表

    vehicleplatenumbers = data['vehicleplatenumber']
    rapid_times = data['rapid_times']
    deceleration_times = data['deceleration_times']
    fatigueDriving_times = data['fatigueDriving_times']
    idlePreheating_times = data['idlePreheating_times']
    overlongIdle_times = data['overlongIdle_times']
    coastingEngineoff_times = data['coastingEngineoff_times']
    speeding_times = data['speeding_times']
    changeRoad_times = data['changeRoad_times']
    safeMiles_flag = data['safeMiles_flag']
    speed_stabilization = data['speed_stabilization']
    lowVisibilitySpeeding_times = data['lowVisibilitySpeeding_times']
    crossWind_time = data['crossWind_time']
    highWind_time = data['highWind_time']
    adverseweatherSpeeding_times = data['adverseweatherSpeeding_times']
    average_speed = data['average_speed']
    againstWind_time = data['againstWind_time']
    diseconomicSpeed_rate = data['diseconomicSpeed_rate']

    for i in range(int(len(data) * 2 / 9)): # 二七分来对汇总文件切分
        trainsetList.append([vehicleplatenumbers[i], rapid_times[i], deceleration_times[i], fatigueDriving_times[i], idlePreheating_times[i],
                            overlongIdle_times[i], coastingEngineoff_times[i], speeding_times[i], changeRoad_times[i], safeMiles_flag[i],
                            speed_stabilization[i], lowVisibilitySpeeding_times[i], crossWind_time[i], highWind_time[i], adverseweatherSpeeding_times[i],
                            average_speed[i], againstWind_time[i], diseconomicSpeed_rate[i]])

    for i in range(int(len(data) * 2 / 9), len(data)):
        testsetList.append([vehicleplatenumbers[i], rapid_times[i], deceleration_times[i], fatigueDriving_times[i], idlePreheating_times[i],
                            overlongIdle_times[i], coastingEngineoff_times[i], speeding_times[i], changeRoad_times[i], safeMiles_flag[i],
                            speed_stabilization[i], lowVisibilitySpeeding_times[i], crossWind_time[i], highWind_time[i], adverseweatherSpeeding_times[i],
                            average_speed[i], againstWind_time[i], diseconomicSpeed_rate[i]])

    # 写入训练集文件
    with open(filepath + '\\trainset.csv', 'w', encoding='utf-8', newline='') as fw1:
        writer = csv.writer(fw1)
        writer.writerows(trainsetList)
    print('训练集文件生成')
    # 写入测试集文件
    with open(filepath + '\\testset.csv', 'w', encoding='utf-8', newline='') as fw2:
        writer = csv.writer(fw2)
        writer.writerows(testsetList)
    print('测试集文件生成')