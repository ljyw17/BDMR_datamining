 # coding=utf-8

from numpy import *
import csv
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 加载数据
def loadDataSet(fileName):  # 解析文件，按tab分割字段，得到一个浮点数字类型的矩阵
     dataMat = []              # 文件的最后一个字段是类别标签
     with open(fileName, 'r', encoding='utf-8') as f:
         readerf = csv.reader(f)
         data_line = list(readerf)
         for data in data_line[1:]:
            dataMat.append(list([float(data[10]), float(data[15])]))
     return dataMat

 # 计算欧几里得距离
def distEclud(vecA, vecB):
     return sqrt(sum(power(vecA - vecB, 2))) # 求两个向量之间的距离

 # 构建聚簇中心，取k个随机质心
def randCent(dataSet, k):
     n = shape(dataSet)[1]
     centroids = mat(zeros((k,n)))   # 每个质心有n个坐标值，总共要k个质心
     for j in range(n):
         minJ = min(dataSet[:,j])
         maxJ = max(dataSet[:,j])
         rangeJ = float(maxJ - minJ)
         centroids[:,j] = minJ + rangeJ * random.rand(k, 1)
     return centroids

 # k-means 聚类算法
def kMeans(dataSet, k, distMeans =distEclud, createCent = randCent):
     m = shape(dataSet)[0]
     clusterAssment = mat(zeros((m,2)))    # 用于存放该样本属于哪类及质心距离
     # clusterAssment第一列存放该数据所属的中心点，第二列是该数据到中心点的距离
     centroids = createCent(dataSet, k)
     clusterChanged = True   # 用来判断聚类是否已经收敛
     while clusterChanged:
         clusterChanged = False;
         for i in range(m):  # 把每一个数据点划分到离它最近的中心点
             minDist = inf; minIndex = -1;
             for j in range(k):
                 distJI = distMeans(centroids[j,:], dataSet[i,:])
                 if distJI < minDist:
                     minDist = distJI; minIndex = j  # 如果第i个数据点到第j个中心点更近，则将i归属为j
             if clusterAssment[i,0] != minIndex: clusterChanged = True;  # 如果分配发生变化，则需要继续迭代
             clusterAssment[i,:] = minIndex,minDist**2   # 并将第i个数据点的分配情况存入字典
         print (centroids)
         for cent in range(k):   # 重新计算中心点
             ptsInClust = dataSet[nonzero(clusterAssment[:,0].A == cent)[0]]   # 去第一列等于cent的所有列
             centroids[cent,:] = mean(ptsInClust, axis = 0)  # 算出这些数据的中心点
     return centroids, clusterAssment


# 取数据的前两维特征作为该条数据的x , y 坐标，
def getXY(dataSet):
    import numpy as np
    m = shape(dataSet)[0]  # 数据集的行
    X = []
    Y = []
    for i in range(m):
        X.append(dataSet[i,0])
        Y.append(dataSet[i,1])
    return np.array(X), np.array(Y)

# 数据可视化
def showCluster(dataSet, k, clusterAssment, centroids):
     fig = plt.figure()
     font = FontProperties(fname=r"D:\BDMR\code\simhei.ttf", size=14)
     plt.title("驾驶倾向性聚类", fontproperties=font)
     ax = fig.add_subplot(111)
     data = []

     for cent in range(k):  # 提取出每个簇的数据
         ptsInClust = dataSet[nonzero(clusterAssment[:, 0].A == cent)[0]]  # 获得属于cent簇的数据
         print(k,ptsInClust,size(ptsInClust))
         data.append(ptsInClust)

     for cent, c, marker in zip(range(k), ['r', 'g', 'b', 'y'], ['^', 'o', '*', 's']):  # 画出数据点散点图
         X, Y = getXY(data[cent])
         ax.scatter(X, Y, s=80, c=c, marker=marker)

     centroidsX, centroidsY = getXY(centroids)
     # ax.scatter(centroidsX, centroidsY, s=1000, c='black', marker='+', alpha=1)  # 画出质心点
     ax.set_xlabel('速度稳定性',fontproperties=font)
     ax.set_ylabel('平均速度', fontproperties=font)
     plt.savefig(r'D:\BDMR\kmeans.jpg')
     plt.show()

if __name__=='__main__':
     # 用测试数据及测试kmeans算法
     datMat = mat(loadDataSet(r'D:\BDMR\testdata3\Gatherfile.csv'))
     myCentroids,clustAssing = kMeans(datMat,3)
     print (myCentroids)
     print (clustAssing)
     showCluster(datMat, 3, clustAssing, myCentroids)