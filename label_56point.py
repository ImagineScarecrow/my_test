from PIL import Image
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import os

filename = "/home/cxb/20211027_data/20211027_night_label/"    #每一个图片标志后存储json的地址
filename2 = "/home/cxb/20211027_data/train.json" # 保存汇总所有标志信息的json地址
#在下面还有一个filename1需要修改，filename1：图片地址
count = os.listdir(filename)

h = []
# 获得从520到1070所有的y坐标点
for i in range(520, 1080, 10):
    h.append(i)

for iz in range(0, len(count)):
    points = []
    with open(filename+count[iz],'r',encoding='utf8')as fp:
        json_data = json.load(fp)
        for i in range(len(json_data['shapes'])):
            points.append(json_data['shapes'][i]['points'])
            points[i] = np.array(points[i]).astype(dtype=int).tolist()
    b = np.array(points)

    # 用于存储计算得到的56个坐标点
    x_y1= []
    x_y = []
    for a in range(len(b)):  # 车道线的条数
        if points[a][0][1]>points[a][1][1]:
            points[a] = list(reversed(points[a]))   #list(reversed(points[a])):用于将list中的元素进行反转
        # 对160到710的y点进行求解x
        for C in range(520,1080,10):
            for d in range(len(points[a])):
                if d ==len(points[a])-1:
                    break
                if C in range(points[a][d][1],points[a][d+1][1]+1):
                    #获得位于points[a][d][1]和points[a][d+1][1]之间的坐标点y
                    # 对C点求对应的x坐标
                    f1 = np.polyfit([points[a][d][1],points[a][d+1][1]],[points[a][d][0],points[a][d+1][0]], 1)
                    p1 = np.poly1d(f1)
                    yvals = p1(C)
                    x_y1.append(int(yvals))
                    break
            if C<points[a][0][1] or C>points[a][len(points[a])-1][1]:
                x_y1.append(-2)
        x_y.append(x_y1)
        x_y1 = []
    filename1 = "2021-10-28_test/"+ count[iz].replace('.json', '.jpg') # 每一张图片对应的地址
    dict = {"lanes": x_y, "h_samples": h, "raw_file": filename1}
    # 存在的问题是dict中的键名字不是双引号
    dict = json.dumps(dict)
    with open(filename2, 'a+') as f:
        f.write(dict+"\n")

