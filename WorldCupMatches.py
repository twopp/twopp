import pandas as pd

df = pd.read_csv("./data/WorldCupMatches.csv")
print(df.shape)
# (852, 19)

df[df.duplicated()]  # 筛选重复值  16个重复值
df = df.drop_duplicates()  # 删除重复项
print(df.shape)
# (836, 19)
# 主队进球数
data1=pd.DataFrame(df.groupby("Home Team Name")["Home Team Goals"].agg(["count",'sum']).sort_values('sum',ascending=False).reset_index())
data1.rename(columns={'Home Team Name': '球队','count': '场次','sum':'进球数'}, inplace=True)
# 客队进球数
data2=pd.DataFrame(df.groupby("Away Team Name")["Away Team Goals"].agg(["count",'sum']).sort_values('sum',ascending=False).reset_index())
data2.rename(columns={'Away Team Name': '球队','count': '场次','sum':'进球数'}, inplace=True)
# 合并
data3=data1.merge(data2,on="球队",how="outer")
data3=data3.fillna(0) # 因为部分球队没有作为主队出场过，所以合并后会有NaN，用0填充
print(data3)

data3["总场次"]=data3["场次_x"]+data3["场次_y"]
data3["总进球数"]=data3["进球数_x"]+data3["进球数_y"]
data3["进球率"]=(data3["总进球数"]/data3["总场次"]).round(2)
print(data3.sort_values("进球率",ascending=False)[:10])
# 主队失球数
data4=pd.DataFrame(df.groupby("Home Team Name")["Away Team Goals"].agg(["count",'sum']).sort_values('sum',ascending=False).reset_index())
data4.rename(columns={'Home Team Name': '球队','count': '场次','sum':'失球数'}, inplace=True)
# 客队失球数
data5=pd.DataFrame(df.groupby("Away Team Name")["Home Team Goals"].agg(["count",'sum']).sort_values('sum',ascending=False).reset_index())
data5.rename(columns={'Away Team Name': '球队','count': '场次','sum':'失球数'}, inplace=True)
# 合并填充
data6=data4.merge(data5,on="球队",how="outer")
data6=data6.fillna(0)
# 失球率
data6["总场次"]=data6["场次_x"]+data6["场次_y"]
data6["总失球数"]=data6["失球数_x"]+data6["失球数_y"]
data6["失球率"]=(data6["总失球数"]/data6["总场次"]).round(2)
data6.sort_values("失球率",ascending=True)[:10]

# 合并数据表
data7 = data3.merge(data6, on="球队", how="outer")
data7 = data7[['球队', '总场次_x', '总进球数', '进球率', '总失球数', '失球率']]
data7.rename(columns={'总场次_x': '总场次'}, inplace=True)
# 画图
import numpy as np

col = ["Brazil", "Italy", "Germany FR", "Argentina", "France", "Uruguay", "England", "Germany", "Spain"]
result = []
for i in col:
    result.append(data7[data7["球队"] == i])
result = np.array(result)
result = result.reshape(9, 6)
result = pd.DataFrame(result, index=col, columns=data7.columns)
result = result.iloc[:, 1:].astype('float')

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = [u'SimHei']
mpl.rcParams['axes.unicode_minus'] = False

minx = min(result["失球率"])
maxx = max(result["失球率"])
miny = min(result["进球率"])
maxy = max(result["进球率"])

plt.figure(figsize=(8, 8), dpi=100)
for i in range(result.shape[0]):
    plt.scatter(x=result["失球率"][i], y=result["进球率"][i], s=result["总场次"][i] * 20, alpha=0.65, cmap='viridis')
plt.xlim(xmin=maxx + 0.1, xmax=minx - 0.1)  # 将失球率从大到小设定X轴
plt.vlines(x=result['失球率'].mean(), ymin=miny - 0.1, ymax=maxy + 0.1,
           colors='black', linewidth=1)
plt.hlines(y=result['进球率'].mean(), xmin=minx - 0.1, xmax=maxx + 0.1,
           colors='black', linewidth=1)
for x, y, z in zip(result["失球率"], result["进球率"], col):
    plt.text(x, y, z, ha='center', fontsize=10)
plt.xlabel("高<—————— 失球率(%) ——————>低", fontsize=15)
plt.ylabel("低<—————— 进球率(%) ——————>高", fontsize=15)
plt.title("夺冠国家进失球率-波士顿矩阵图", fontsize=20)
plt.show()