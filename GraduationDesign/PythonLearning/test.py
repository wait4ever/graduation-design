# 杨辉三角
# def triangle():
#     n = 0
#     L = [1]
#     while True:
#         yield L
#         L = [1] + [L[i]+L[i+1] for i in range(len(L)-1)]+[1]
# for i in triangle():
#     print(i)

#reduce 用法
# from functools import reduce
# def mutiple(x,y):
#     return x*y
# L = [1,2,3,4]
# print(reduce(mutiple,L))

#map用法
# def normalize(name):
#     return name[0:1].upper()+name[1:].lower()  # 字符串切片和大小写修改
#
# L1 = ['adam', 'LISA', 'barT']
# L2 = list(map(normalize, L1))
# print(L2)


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from functools import reduce
# def StrtoNum(x):
#     StrtoNum2 = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}
#     return StrtoNum2[x]
#
# def aaa(x,y):
#     return x*10+y
#
# def bbb(x):
#     return x/10
#
# def str2float(s):
#     point = s.find('.')
#     return reduce(aaa,map(StrtoNum,s[:point]))+reduce(bbb,map(StrtoNum,s[point+1:]))

# print(str2float('123.456'))
# print('str2float(\'123.456\') =', str2float('123.456'))
# if abs(str2float('123.456') - 123.456) < 0.00001:
#     print('测试成功!')
# else:
#     print('测试失败!')





# L = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]
# def by_name(t):
#     return t[1]*-1
#
# L2 = sorted(L, key=by_name)
# print(L2)
from sqlalchemy import create_engine
import pymysql
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
weiboId = '4366834524273242'
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='textanalyser')
conn.autocommit(True)
cur = conn.cursor()

sql_male_pos = "select count(*) from comment_info where userGender='m' and sentiment>=0 and weiboId='"+weiboId+"'"
cur.execute(sql_male_pos)
male_pos= cur.fetchone()[0]

sql_male_neg = "select count(*) from comment_info where userGender='m' and sentiment<0 and weiboId='"+weiboId+"'"
cur.execute(sql_male_neg)
male_neg= cur.fetchone()[0]

sql_female_pos = "select count(*) from comment_info where userGender='f' and sentiment>=0 and weiboId='"+weiboId+"'"
cur.execute(sql_female_pos)
female_pos= cur.fetchone()[0]

sql_female_neg = "select count(*) from comment_info where userGender='f' and sentiment<0 and weiboId='"+weiboId+"'"
cur.execute(sql_female_neg)
female_neg= cur.fetchone()[0]

cur.close()
conn.close()

## 使用matplotlib制作饼图
labels = ['男积极','男消极','女积极','女消极']
data= [male_pos,male_neg,female_neg,female_pos]
plt.pie(data, labels=labels, autopct='%1.2f%%')
plt.axis('equal')

# plt.legend(loc = 'center left')
plt.title("男女比例对比饼图",loc ='left')
plt.savefig("D:/"+weiboId+"_fm.jpg")
plt.show()
