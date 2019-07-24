# -*- coding: utf-8 -*-

import math
import random
import pandas as pd
import numpy as np

random.seed(0)
def rand(a, b):
    return (b - a) * random.random() + a


def make_matrix(m, n, fill=0.0):  # 创造一个指定大小的矩阵
    mat = []
    for i in range(m):
        mat.append([fill] * n)
    return mat

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def sigmod_derivate(x):
    return x * (1 - x)

def deal_maxmin(serialdataframe):
    "归一化"
    max_min_scaler = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))

    for i in range(len(serialdataframe)):
        if(serialdataframe.iloc[i][0] != 0): #只有不是全为零的情况才进行归一化
            return serialdataframe.apply(max_min_scaler)
    return serialdataframe

class Bpnn:

    def setup(self, ni, nh, no):
        self.input_n = ni + 1
        self.hidden_n = nh
        self.output_n = no
        # init cells
        self.input_cells = [1.0] * self.input_n
        self.hidden_cells = [1.0] * self.hidden_n
        self.output_cells = [1.0] * self.output_n
        # 初始化权重
        self.input_weights = make_matrix(self.input_n, self.hidden_n)
        self.output_weights = make_matrix(self.hidden_n, self.output_n)
        # random activate
        for i in range(self.input_n):
            for h in range(self.hidden_n):
                self.input_weights[i][h] = rand(-0.2, 0.2)
        for h in range(self.hidden_n):
            for o in range(self.output_n):
                self.output_weights[h][o] = rand(-2.0, 2.0)
        # init correction matrix
        self.input_correction = make_matrix(self.input_n, self.hidden_n)
        self.output_correction = make_matrix(self.hidden_n, self.output_n)

    def predict(self, inputs):
        # 激励输入层
        for i in range(self.input_n - 1):
            self.input_cells[i] = inputs[i]
        # 激励隐藏层
        for j in range(self.hidden_n):
            total = 0.0
            for i in range(self.input_n):
                total += self.input_cells[i] * self.input_weights[i][j]
            self.hidden_cells[j] = sigmoid(total)
        # 激励输出层
        for k in range(self.output_n):
            total = 0.0
            for j in range(self.hidden_n):
                total += self.hidden_cells[j] * self.output_weights[j][k]
            self.output_cells[k] = sigmoid(total)
        return self.output_cells[:]

    def back_propagate(self, case, label, learn, correct):
        # feed forward
        self.predict(case)
        # 输出层错误
        output_deltas = [0.0] * self.output_n
        for o in range(self.output_n):
            error = label[o] - self.output_cells[o]
            output_deltas[o] = sigmod_derivate(self.output_cells[o]) * error
        # get hidden layer error
        hidden_deltas = [0.0] * self.hidden_n
        for h in range(self.hidden_n):
            error = 0.0
            for o in range(self.output_n):
                error += output_deltas[o] * self.output_weights[h][o]
            hidden_deltas[h] = sigmod_derivate(self.hidden_cells[h]) * error
        # 更新输出权重
        for h in range(self.hidden_n):
            for o in range(self.output_n):
                change = output_deltas[o] * self.hidden_cells[h]
                self.output_weights[h][o] += learn * change + correct * self.output_correction[h][o]
                self.output_correction[h][o] = change
        # 更新输入权重
        for i in range(self.input_n):
            for h in range(self.hidden_n):
                change = hidden_deltas[h] * self.input_cells[i]
                self.input_weights[i][h] += learn * change + correct * self.input_correction[i][h]
                self.input_correction[i][h] = change
        # 全局错误
        error = 0.0
        for o in range(len(label)):
            error += 0.5 * (label[o] - self.output_cells[o]) ** 2
        return error

    def train(self, cases, labels, limit=10000, learn=0.05, correct=0.1):
        for i in range(limit):
            error = 0.0
            for i in range(len(cases)):
                label = labels[i]
                case = cases[i]
                error += self.back_propagate(case, label, learn, correct)

def getAvgerror(numlist1, numlist2):
    '得到两序列间的平均距离，这里用作求平均误差'
    totalerror = 0
    for i in range(len(numlist1)):
        totalerror += abs(numlist1[i]-numlist2[i])
    return totalerror/len(numlist1)
#
# def getParameter(cases, labels):
#     '求出最佳参数：隐层神经元个数与学习率'
#     bp = Bpnn()
#     imputnum = len(cases[0])
#     casetrain1 = []
#     casetrain2 = [] # 验证集，用来修正
#     labeltrain1 = []
#     labeltrain2 = [] # 验证集，用来修正
#     predict_results = []
#     for i in range(len(cases)):
#         if i < len(cases)*7/10: #七三分
#             casetrain1.append(cases[i])
#             labeltrain1.append(labels[i])
#         else:
#             casetrain2.append(cases[i])
#             labeltrain2.append(labels[i][0]*100)
#
#     bestnnum = int(imputnum/2)
#     bestlrate = 0.01
#     bp.setup(imputnum, bestnnum, 1)
#     bp.train(cases, labels, 5000, bestlrate, 0.1)
#     for case in casetrain2:
#         predict_results.append(bp.predict(case)[0]*100)
#     minerror = getAvgerror(labeltrain2, predict_results)
#
#     for nnum in range(int(imputnum/2), imputnum+1):# 神经元个数从输入层大小的一半开始，到输入层大小停止迭代
#         for lrate in np.arange(0.01, 0.5+0.01, 0.01): # 学习率从0.01开始迭代，步长为0.01
#             predict_results = []
#             bp.setup(imputnum, nnum, 1)
#             bp.train(cases, labels, 5000, lrate, 0.1)
#             for case in casetrain2:
#                 predict_results.append(bp.predict(case)[0] * 100)
#             if getAvgerror(labeltrain2, predict_results) < minerror: # 如果找到更小的平均错误数，更新
#                 minerror = getAvgerror(labeltrain2, predict_results)
#                 bestnnum = nnum
#                 bestlrate = lrate
#                 print("正在调参，当前最小平均误差为{}，神经元个数为{}，学习率为{:.2f}".format(minerror, bestnnum, bestlrate))
#     return bestnnum, bestlrate

def keyinTotalscore(traindata, testdata):
    nn = Bpnn()
    cases = []
    labels = []
    predict_list = []
    predict_totalscores = []

    # 训练集和测试集一起归一化
    rapid_frame = deal_maxmin(pd.concat([traindata[['rapid_times']], testdata[['rapid_times']]]))
    deceleration_frame = deal_maxmin(pd.concat([traindata[['deceleration_times']], testdata[['deceleration_times']]]))
    fatigueDriving_frame = deal_maxmin(pd.concat([traindata[['fatigueDriving_times']], testdata[['fatigueDriving_times']]]))
    idlePreheating_frame = deal_maxmin(pd.concat([traindata[['idlePreheating_times']], testdata[['idlePreheating_times']]]))
    overlongIdle_frame = deal_maxmin(pd.concat([traindata[['overlongIdle_times']], testdata[['overlongIdle_times']]]))
    coastingEngineoff_frame = deal_maxmin(pd.concat([traindata[['coastingEngineoff_times']], testdata[['coastingEngineoff_times']]]))
    speeding_frame = deal_maxmin(pd.concat([traindata[['speeding_times']], testdata[['speeding_times']]]))
    changeRoad_frame = deal_maxmin(pd.concat([traindata[['changeRoad_times']], testdata[['changeRoad_times']]]))
    safeMiles_frame = deal_maxmin(pd.concat([traindata[['safeMiles_flag']], testdata[['safeMiles_flag']]]))
    speed_stabilization_frame = deal_maxmin(pd.concat([traindata[['speed_stabilization']], testdata[['speed_stabilization']]]))
    lowVisibilitySpeeding_frame = deal_maxmin(pd.concat([traindata[['lowVisibilitySpeeding_times']], testdata[['lowVisibilitySpeeding_times']]]))
    crossWind_frame = deal_maxmin(pd.concat([traindata[['crossWind_time']], testdata[['crossWind_time']]]))
    highWind_frame = deal_maxmin(pd.concat([traindata[['highWind_time']], testdata[['highWind_time']]]))
    adverseweatherSpeeding_frame = deal_maxmin(pd.concat([traindata[['adverseweatherSpeeding_times']], testdata[['adverseweatherSpeeding_times']]]))
    average_speed_frame = deal_maxmin(pd.concat([traindata[['average_speed']], testdata[['average_speed']]]))
    againstWind_frame = deal_maxmin(pd.concat([traindata[['againstWind_time']], testdata[['againstWind_time']]]))
    diseconomicSpeed_frame = deal_maxmin(pd.concat([traindata[['diseconomicSpeed_rate']], testdata[['diseconomicSpeed_rate']]]))
    # 分表
    rapid_times = rapid_frame[0:len(traindata)]
    rapid_times2 = rapid_frame[len(traindata):len(traindata) + len(testdata)]
    deceleration_times = deceleration_frame[0:len(traindata)]
    deceleration_times2 = deceleration_frame[len(traindata):len(traindata) + len(testdata)]
    fatigueDriving_times = fatigueDriving_frame[0:len(traindata)]
    fatigueDriving_times2 = fatigueDriving_frame[len(traindata):len(traindata) + len(testdata)]
    idlePreheating_times = idlePreheating_frame[0:len(traindata)]
    idlePreheating_times2 = idlePreheating_frame[len(traindata):len(traindata) + len(testdata)]
    overlongIdle_times = overlongIdle_frame[0:len(traindata)]
    overlongIdle_times2 = overlongIdle_frame[len(traindata):len(traindata) + len(testdata)]
    coastingEngineoff_times = coastingEngineoff_frame[0:len(traindata)]
    coastingEngineoff_times2 = coastingEngineoff_frame[len(traindata):len(traindata) + len(testdata)]
    speeding_times = speeding_frame[0:len(traindata)]
    speeding_times2 = speeding_frame[len(traindata):len(traindata) + len(testdata)]
    changeRoad_times = changeRoad_frame[0:len(traindata)]
    changeRoad_times2 = changeRoad_frame[len(traindata):len(traindata) + len(testdata)]
    safeMiles_flag = safeMiles_frame[0:len(traindata)]
    safeMiles_flag2 = safeMiles_frame[len(traindata):len(traindata) + len(testdata)]
    speed_stabilization = speed_stabilization_frame[0:len(traindata)].values.flatten().tolist()  # 对速度稳定性特殊处理，取与1的距离
    speed_stabilization = [1 - float(i) for i in speed_stabilization]
    speed_stabilization = pd.DataFrame(speed_stabilization, columns=['speed_stabilization'])
    speed_stabilization2 = speed_stabilization_frame[len(traindata):len(traindata) + len(testdata)].values.flatten().tolist()  # 对速度稳定性特殊处理，取与1的距离
    speed_stabilization2 = [1 - float(i) for i in speed_stabilization2]
    speed_stabilization2 = pd.DataFrame(speed_stabilization2, columns=['speed_stabilization'])
    lowVisibilitySpeeding_times = lowVisibilitySpeeding_frame[0:len(traindata)]
    lowVisibilitySpeeding_times2 = lowVisibilitySpeeding_frame[len(traindata):len(traindata) + len(testdata)]
    crossWind_time = crossWind_frame[0:len(traindata)]
    crossWind_time2 = crossWind_frame[len(traindata):len(traindata) + len(testdata)]
    highWind_time = highWind_frame[0:len(traindata)]
    highWind_time2 = highWind_frame[len(traindata):len(traindata) + len(testdata)]
    adverseweatherSpeeding_times = adverseweatherSpeeding_frame[0:len(traindata)]
    adverseweatherSpeeding_times2 = adverseweatherSpeeding_frame[len(traindata):len(traindata) + len(testdata)]
    average_speed = average_speed_frame[0:len(traindata)].values.flatten().tolist()  # 对平均速度特殊处理，取与1的距离
    average_speed = [1 - float(i) for i in average_speed]
    average_speed = pd.DataFrame(average_speed, columns=['average_speed'])
    average_speed2 = average_speed_frame[len(traindata):len(traindata) + len(testdata)].values.flatten().tolist()  # 对平均速度特殊处理，取与1的距离
    average_speed2 = [1 - float(i) for i in average_speed2]
    average_speed2 = pd.DataFrame(average_speed2, columns=['average_speed'])
    againstWind_time = againstWind_frame[0:len(traindata)]
    againstWind_time2 = againstWind_frame[len(traindata):len(traindata) + len(testdata)]
    diseconomicSpeed_rate = diseconomicSpeed_frame[0:len(traindata)]
    diseconomicSpeed_rate2 = diseconomicSpeed_frame[len(traindata):len(traindata) + len(testdata)]

    totalResults = traindata['totalscore']
    # 训练集与打分的dataframe
    for i in range(len(traindata)):
        templist = [rapid_times.iloc[i][0], deceleration_times.iloc[i][0], fatigueDriving_times.iloc[i][0],
                    idlePreheating_times.iloc[i][0], overlongIdle_times.iloc[i][0], coastingEngineoff_times.iloc[i][0], speeding_times.iloc[i][0],
                    changeRoad_times.iloc[i][0], safeMiles_flag.iloc[i][0], speed_stabilization.iloc[i][0], lowVisibilitySpeeding_times.iloc[i][0],
                    crossWind_time.iloc[i][0], highWind_time.iloc[i][0], adverseweatherSpeeding_times.iloc[i][0], average_speed.iloc[i][0],
                    againstWind_time.iloc[i][0], diseconomicSpeed_rate.iloc[i][0]]

        cases.append(templist)

        labels.append([totalResults[i] * 0.01])

    # neuron_num, learn_rate = getParameter(cases, labels) # 求得最佳超参数
    nn.setup(17, 27, 1)
    nn.train(cases, labels, 10000, 0.1, 0.1)
    # 测试集的dataframe
    for i in range(len(testdata)):
        predict_templist = [rapid_times2.iloc[i][0], deceleration_times2.iloc[i][0], fatigueDriving_times2.iloc[i][0],
                            idlePreheating_times2.iloc[i][0], overlongIdle_times2.iloc[i][0], coastingEngineoff_times2.iloc[i][0],
                            speeding_times2.iloc[i][0], changeRoad_times2.iloc[i][0], safeMiles_flag2.iloc[i][0], speed_stabilization2.iloc[i][0],
                            lowVisibilitySpeeding_times2.iloc[i][0], crossWind_time2.iloc[i][0], highWind_time2.iloc[i][0], adverseweatherSpeeding_times2.iloc[i][0],
                            average_speed2.iloc[i][0], againstWind_time2.iloc[i][0], diseconomicSpeed_rate2.iloc[i][0]]
        predict_list.append(predict_templist)

    # 计算每一行的综合得分
    for case in predict_list:
        predict_totalscores.append(nn.predict(case)[0] * 100)

    print(predict_totalscores)
    testdata['totalscorebyPredict'] = predict_totalscores
    testdata.to_csv(testfile, encoding="utf_8_sig", index=0)
    print("综合评分已计算完成并写入文件")

def keyinSafescore(traindata,testdata):
    nn = Bpnn()
    cases = []
    labels = []
    predict_list = []
    predict_totalscores = []

    # 训练集和测试集一起归一化
    rapid_frame = deal_maxmin(pd.concat([traindata[['rapid_times']], testdata[['rapid_times']]]))
    deceleration_frame = deal_maxmin(pd.concat([traindata[['deceleration_times']], testdata[['deceleration_times']]]))
    fatigueDriving_frame = deal_maxmin(pd.concat([traindata[['fatigueDriving_times']], testdata[['fatigueDriving_times']]]))
    idlePreheating_frame = deal_maxmin(pd.concat([traindata[['idlePreheating_times']], testdata[['idlePreheating_times']]]))
    overlongIdle_frame = deal_maxmin(pd.concat([traindata[['overlongIdle_times']], testdata[['overlongIdle_times']]]))
    coastingEngineoff_frame = deal_maxmin(pd.concat([traindata[['coastingEngineoff_times']], testdata[['coastingEngineoff_times']]]))
    speeding_frame = deal_maxmin(pd.concat([traindata[['speeding_times']], testdata[['speeding_times']]]))
    changeRoad_frame = deal_maxmin(pd.concat([traindata[['changeRoad_times']], testdata[['changeRoad_times']]]))
    safeMiles_frame = deal_maxmin(pd.concat([traindata[['safeMiles_flag']], testdata[['safeMiles_flag']]]))
    speed_stabilization_frame = deal_maxmin(pd.concat([traindata[['speed_stabilization']], testdata[['speed_stabilization']]]))
    lowVisibilitySpeeding_frame = deal_maxmin(pd.concat([traindata[['lowVisibilitySpeeding_times']], testdata[['lowVisibilitySpeeding_times']]]))
    crossWind_frame = deal_maxmin(pd.concat([traindata[['crossWind_time']], testdata[['crossWind_time']]]))
    highWind_frame = deal_maxmin(pd.concat([traindata[['highWind_time']], testdata[['highWind_time']]]))
    adverseweatherSpeeding_frame = deal_maxmin(pd.concat([traindata[['adverseweatherSpeeding_times']], testdata[['adverseweatherSpeeding_times']]]))
    average_speed_frame = deal_maxmin(pd.concat([traindata[['average_speed']], testdata[['average_speed']]]))
    againstWind_frame = deal_maxmin(pd.concat([traindata[['againstWind_time']], testdata[['againstWind_time']]]))
    diseconomicSpeed_frame = deal_maxmin(pd.concat([traindata[['diseconomicSpeed_rate']], testdata[['diseconomicSpeed_rate']]]))
    # 分表
    rapid_times = rapid_frame[0:len(traindata)]
    rapid_times2 = rapid_frame[len(traindata):len(traindata) + len(testdata)]
    deceleration_times = deceleration_frame[0:len(traindata)]
    deceleration_times2 = deceleration_frame[len(traindata):len(traindata) + len(testdata)]
    fatigueDriving_times = fatigueDriving_frame[0:len(traindata)]
    fatigueDriving_times2 = fatigueDriving_frame[len(traindata):len(traindata) + len(testdata)]
    idlePreheating_times = idlePreheating_frame[0:len(traindata)]
    idlePreheating_times2 = idlePreheating_frame[len(traindata):len(traindata) + len(testdata)]
    overlongIdle_times = overlongIdle_frame[0:len(traindata)]
    overlongIdle_times2 = overlongIdle_frame[len(traindata):len(traindata) + len(testdata)]
    coastingEngineoff_times = coastingEngineoff_frame[0:len(traindata)]
    coastingEngineoff_times2 = coastingEngineoff_frame[len(traindata):len(traindata) + len(testdata)]
    speeding_times = speeding_frame[0:len(traindata)]
    speeding_times2 = speeding_frame[len(traindata):len(traindata) + len(testdata)]
    changeRoad_times = changeRoad_frame[0:len(traindata)]
    changeRoad_times2 = changeRoad_frame[len(traindata):len(traindata) + len(testdata)]
    safeMiles_flag = safeMiles_frame[0:len(traindata)]
    safeMiles_flag2 = safeMiles_frame[len(traindata):len(traindata) + len(testdata)]
    speed_stabilization = speed_stabilization_frame[0:len(traindata)].values.flatten().tolist() # 对速度稳定性特殊处理，取与1的距离
    speed_stabilization = [1-float(i) for i in speed_stabilization]
    speed_stabilization = pd.DataFrame(speed_stabilization, columns=['speed_stabilization'])
    speed_stabilization2 = speed_stabilization_frame[len(traindata):len(traindata) + len(testdata)].values.flatten().tolist() # 对速度稳定性特殊处理，取与1的距离
    speed_stabilization2 = [1 - float(i) for i in speed_stabilization2]
    speed_stabilization2 = pd.DataFrame(speed_stabilization2, columns=['speed_stabilization'])
    lowVisibilitySpeeding_times = lowVisibilitySpeeding_frame[0:len(traindata)]
    lowVisibilitySpeeding_times2 = lowVisibilitySpeeding_frame[len(traindata):len(traindata) + len(testdata)]
    crossWind_time = crossWind_frame[0:len(traindata)]
    crossWind_time2 = crossWind_frame[len(traindata):len(traindata) + len(testdata)]
    highWind_time = highWind_frame[0:len(traindata)]
    highWind_time2 = highWind_frame[len(traindata):len(traindata) + len(testdata)]
    adverseweatherSpeeding_times = adverseweatherSpeeding_frame[0:len(traindata)]
    adverseweatherSpeeding_times2 = adverseweatherSpeeding_frame[len(traindata):len(traindata) + len(testdata)]

    safeResults = traindata['safescore']
    # 训练集及结果得分的dataframe
    for i in range(len(traindata)):
        templist = [rapid_times.iloc[i][0], deceleration_times.iloc[i][0], fatigueDriving_times.iloc[i][0],
                    idlePreheating_times.iloc[i][0], overlongIdle_times.iloc[i][0], coastingEngineoff_times.iloc[i][0], speeding_times.iloc[i][0],
                    changeRoad_times.iloc[i][0], safeMiles_flag.iloc[i][0], speed_stabilization.iloc[i][0], lowVisibilitySpeeding_times.iloc[i][0],
                    crossWind_time.iloc[i][0], highWind_time.iloc[i][0], adverseweatherSpeeding_times.iloc[i][0]]

        cases.append(templist)

        labels.append([safeResults[i] * 0.01])

    # neuron_num, learn_rate = getParameter(cases, labels) # 求得最佳超参数
    nn.setup(14, 22, 1)
    nn.train(cases, labels, 10000, 0.1, 0.1)

    for i in range(len(testdata)):
        predict_templist = [rapid_times2.iloc[i][0], deceleration_times2.iloc[i][0], fatigueDriving_times2.iloc[i][0],
                            idlePreheating_times2.iloc[i][0], overlongIdle_times2.iloc[i][0], coastingEngineoff_times2.iloc[i][0],
                            speeding_times2.iloc[i][0], changeRoad_times2.iloc[i][0], safeMiles_flag2.iloc[i][0], speed_stabilization2.iloc[i][0],
                            lowVisibilitySpeeding_times2.iloc[i][0], crossWind_time2.iloc[i][0], highWind_time2.iloc[i][0], adverseweatherSpeeding_times2.iloc[i][0]]
        predict_list.append(predict_templist)

    for case in predict_list:
        predict_totalscores.append(nn.predict(case)[0] * 100)

    print(predict_totalscores)
    testdata['safescorebyPredict'] = predict_totalscores
    testdata.to_csv(testfile, encoding="utf_8_sig", index=0)
    print("安全评分已计算完成并写入文件")

if __name__ == '__main__':

    trainfile = r'D:\BDMR\testdata\trainset.csv'
    traindata = pd.read_csv(trainfile, low_memory=False)
    testfile = r'D:\BDMR\testdata\testset.csv'
    testdata = pd.read_csv(testfile, low_memory=False)
    keyinSafescore(traindata, testdata)
    keyinTotalscore(traindata, testdata)