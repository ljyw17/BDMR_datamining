# -*- coding: utf-8 -*-

import os, folium, glob, csv
import pandas as pd
from folium.plugins import HeatMap

def deleteDuplicates(file):
    "利用pandas进行去重"
    df = pd.read_csv(file, header = 0, low_memory=False)
    dataframe = df.drop_duplicates()
    dataframe.to_csv(file, encoding="utf_8_sig", index = 0)

def appendData(data, file):
    "画热力图"
    deleteDuplicates(file)  # 调用去重函数

    with open(file, encoding = "utf-8") as f:
        reader = csv.reader(f)
        reader = list(reader)
        for row in reader[1:]:
            data.append(list([float(row[4]), float(row[3]), 0.000001]))
    return data

if __name__=="__main__":
    data = []
    filelist = glob.glob(r'D:\BDMR\testdata\*dealed.csv')
    for file in filelist: #循环读取待处理文件
        if((filelist.index(file) + 1)%4==0):
            print("正在添加第{}个文件的经纬度".format(filelist.index(file) + 1))
            data = appendData(data, file)

    m = folium.Map([35, 113], tiles='stamentoner', zoom_start=5)
    HeatMap(data).add_to(m)
    m.save(os.path.join(r'D:\BDMR\code\extra code', 'Heatmap.html'))
    print("热力图生成成功")