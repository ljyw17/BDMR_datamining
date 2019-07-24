# -*- coding: utf-8 -*-

import os, datetime, folium, csv, os, pygame, glob
from folium import plugins
import pandas as pd
import numpy as np
import pygame
from pygame.locals import *

# 急加速情况的经纬度
rapid_lngs = []
rapid_lats = []
decelerate_lngs = []
decelerate_lats = []

def get_diff_time(time1,time2):
    t1_year, t1_month, t1_day, t1_hour, t1_min, t1_sec = split_time(time1)
    t2_year, t2_month, t2_day, t2_hour, t2_min, t2_sec = split_time(time2)
    d1 = datetime.datetime(int(t1_year), int(t1_month), int(t1_day), int(t1_hour), int(t1_min), int(t1_sec))
    d2 = datetime.datetime(int(t2_year), int(t2_month), int(t2_day), int(t2_hour), int(t2_min), int(t2_sec))
    sec = (d2 - d1).total_seconds()
    return sec

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

def rapid(time1, time2, speed1, speed2, lng, lat):
    t1_year, t1_month, t1_day, t1_hour, t1_min, t1_sec = split_time(time1)
    t2_year, t2_month, t2_day, t2_hour, t2_min, t2_sec = split_time(time2)
    d1 = datetime.datetime(int(t1_year), int(t1_month), int(t1_day), int(t1_hour), int(t1_min), int(t1_sec))
    d2 = datetime.datetime(int(t2_year), int(t2_month), int(t2_day), int(t2_hour), int(t2_min), int(t2_sec))
    sec = (d2 - d1).total_seconds()
    a = speed2 - speed1
    if sec == 1 or sec == 2 or sec == 3:
        if a / sec >= 10.8:
            if len(rapid_lats) == 0 and len(rapid_lngs) == 0:
                rapid_lngs.append(lng)
                rapid_lats.append(lat)
            elif lng != rapid_lngs[-1] and lat != rapid_lats[-1]:
                rapid_lngs.append(lng)
                rapid_lats.append(lat)
            # 返回急加速的经纬度
        elif a / sec < -10.8:
            if len(decelerate_lats) == 0:
                decelerate_lngs.append(lng)
                decelerate_lats.append(lat)
            elif  lng != decelerate_lngs[-1] and lat != decelerate_lats[-1]:
                decelerate_lngs.append(lng)
                decelerate_lats.append(lat)

def getInfo(filename):
    with open(filename, 'r', encoding = 'utf-8') as f:
        readerf = csv.reader(f)
        data_line = list(readerf)
        num = 0
        # 分行读取其中的经纬度，在传到地图中显示
        lngs = []
        lats = []
        times = []
        speeds = []
        mileages = []
        dul_miles = []
        avg_time = []
        avg_times = []
        avg_speed = []
        spare_times = 0

        for data in data_line[1:]:
            lng = data[3]
            lat = data[4]
            time = data[10]
            speed = data[11]
            mileage = data[12]

            mileage = float(mileage)
            mileages.append(mileage)
            speed = float(speed)
            if speed == 0:
                num = num + 1
            lng = float(lng)
            lat = float(lat)
            avg_time.append(time)
            if len(mileages) > 2:
                if get_diff_time(avg_time[-2], avg_time[-1]) > 20 and (mileages[-2] == mileages[-1]):
                    spare_times += get_diff_time(avg_time[-2], avg_time[-1])
            if lng == 0:
                print('零值', num)
                print(spare_times)
                mile = mileages[-2] - mileages[0]
                print('总长度为', len(avg_time))
                print(avg_time[0], avg_time[-2])
                sec = get_diff_time(avg_time[0], avg_time[-2])
                print('总时间为', sec)
                sec = sec - num - spare_times
                print('行驶时间为', sec)
                hour = round(sec / (60*60), 6)
                if hour ==0:
                    hour = 100
                avg_times.append(hour)
                print('里程', mile)
                dul_miles.append(mile)
                avg_speed.append(mile / hour)
                mileages = []
                avg_time = []
                num = 0
                spare_times = 0

            if len(lngs) == 0 and len(lats) == 0:
                lngs.append(lng)
                lats.append(lat)
            elif lng != lngs[-1] and lat != lats[-1]:
                lngs.append(lng)
                lats.append(lat)
                if len(times) == 0 and len(speeds) == 0:
                    times.append(time)
                    speeds.append(speed)
                else:
                    times.append(time)
                    speeds.append(speed)
                    rapid(times[0], times[1], speeds[0], speeds[1], lng, lat)
                    times.pop(0)
                    speeds.pop(0)
    return rapid_lngs, rapid_lats, decelerate_lngs, decelerate_lats, dul_miles, avg_speed

def read_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    lngs = data['lng']
    lats = data['lat']
    return lngs, lats

def to_unicode(string):
    ret = ''
    for v in string:
        ret = ret + hex(ord(v)).upper().replace('0X', '\\u')

    return ret

def drawline(filename):
    '''
    利用folium绘制轨迹,并生成html文件
    '''
    filepath, fullflname = os.path.split(filename)
    fname, ext = os.path.splitext(fullflname)
    coordinate_list = []
    index_i = 0
    appendnum = 0
    lngs, lats = read_data(filename)
    setlat = set(lats)
    lats2 = list(setlat)
    lats2.sort()
    maxlng, minlat = max(lngs), lats2[1] # 得到最大的经纬和最小的纬度，用于后面图片的添加
    rapid_lngs, rapid_lats, decelerate_lngs, decelerate_lats, miles, speed = getInfo(filename)

    m = folium.Map([(lats[0]+lats[len(lats)-2]) / 2, (lngs[0]+lngs[len(lngs)-2]) / 2], zoom_start=11, control_scale=True)
    location = np.zeros((len(lngs), 2))
    for i in range(len(lngs)):
        location[i][1] = lngs[i]
        location[i][0] = lats[i]
    lo = location.tolist()


    for lat, lng in lo:
        if lat != 0:
            coordinate_list.append(list((lat, lng)))
            prelat, prelng = lat, lng
        else:
            route = folium.PolyLine(  # polyline方法将坐标用线段形式连接起来
                # lo,  # 将坐标点连接起来
                coordinate_list,
                weight = 5,  # 线的大小
                color = 'green',  # 线的颜色
                opacity = 1  # 线的透明度
            )
            if miles[index_i] > 5:
                route.add_to(m)
                appendnum += 1
                pygame.init() # pygame初始化
                text = "第{}段：distance:{}km average speed:{}km/h".format(appendnum, miles[index_i], float('%.2f' % speed[index_i]))

                # 设置字体和字号
                font = pygame.font.Font('simhei.ttf', 68)
                # 渲染图片，设置背景颜色和字体样式,前面的颜色是字体颜色
                ftext = font.render(text, True, (0, 0, 0), (236, 231, 213))
                # 保存图片
                pygame.image.save(ftext, os.getcwd() + '\img\\' + fname + "_traverse{}.jpg".format(index_i+1))  # 图片保存地址
                folium.raster_layers.ImageOverlay(os.getcwd() + '\img\\' + fname + "_traverse{}.jpg".format(index_i+1),
                                                  [[minlat, maxlng], [minlat-0.03, maxlng + 0.65]]).add_to(m)
                minlat -= 0.031

                for lat, lng in zip(rapid_lats, rapid_lngs):
                    if list((lat, lng)) in coordinate_list:
                        folium.Circle(
                            radius=500,
                            location=[lat, lng],
                            popup= str(lat) + ',' + str(lng),
                            color='crimson',
                            fill=False,
                        ).add_to(m)

                for lat, lng in zip(decelerate_lats, decelerate_lngs):
                    if list((lat, lng)) in coordinate_list:
                        folium.Marker([lat, lng], icon=folium.Icon(icon='')).add_to(m)
            coordinate_list = []
            index_i += 1


    m.save(os.path.join(os.getcwd() + '\html' , '{}_trajectory.html'.format(fname)))
    with open(os.path.join(os.getcwd() + '\html' , '{}_trajectory.html'.format(fname)), "r", encoding="utf-8") as f:
        #readlines以列表的形式将文件读出
        html = ''.join(f.readlines())
        # html = html.replace('https://cdn.jsdelivr.net/npm/leaflet@1.4.0/dist/leaflet.js','js_css/leaflet.js')
        # html = html.replace('https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js', 'js_css/leaflet.awesome-markers.js')
        # html = html.replace('https://cdn.jsdelivr.net/npm/leaflet@1.4.0/dist/leaflet.css','js_css/leaflet.css')
        html = html.replace('</body>', '<div id="dg" style="z-index: 999; position: fixed ! important; right: 0px; bottom: 20px;"> <img src="..\img\sign.png" width="105" height="80" /> </div></body>')
    with open(os.path.join(os.getcwd() + '\html', '{}_trajectory.html'.format(fname)), "w", encoding='utf-8') as fw:
        fw.writelines(html)
    print("轨迹页面生成成功")


if __name__ == '__main__':

    filelist = glob.glob(r'D:\BDMR\10tables\*dealed.csv')
    for file in filelist: #循环读取待处理文件
        print("正在处理第{}个文件".format(filelist.index(file) + 1))
        drawline(file)



    # 测试
    # filename = (r'D:\BDMR\10tables\originaldata\AD00053dealed.csv')
    # drawline(filename)