from collections import defaultdict
import pandas as pd
import jieba
import codecs
from sqlalchemy import create_engine
import pymysql
from sys import argv
import trainModel_dic
import matplotlib.pyplot as plt
"""
1. 文本切割
"""



def seg_word(sentence):
    """使用jieba对文档分词"""
    seg_list = jieba.cut(sentence)
    seg_result = []
    for w in seg_list:
        seg_result.append(w)
    # 读取停用词文件
    stopwords = set()
    fr = codecs.open('D:/Desktop/Desktop/GraduationDesign/stopwordsHIT.txt', 'r', 'utf-8')
    for word in fr:
        stopwords.add(word.strip())
    fr.close()
    # 去除停用词
    return list(filter(lambda x: x not in stopwords, seg_result))


# def classifyWords(wordDict):
#     # (1) 情感词
#     with open('BosonNLP_sentiment_score.txt', 'r', encoding='UTF-8') as f:
#
#         senList = f.readlines()
#         print(senList)
#     senDict = defaultdict()
#     index = 1
#     for s in senList:
#         senDict[s.split(' ')[0]] = s.split(' ')[1]
#         index = index +1
#         if index >10 :
#             break
#         # (2) 否定词
#     with open('notDict.txt', 'r', encoding='UTF-8') as f:
#         notList = f.readlines()
#          # (3) 程度副词
#     f = open('degreeDict.txt')
#     degreeList = f.readLines()
#     degreeDict = defaultdict()
#     for d in degreeList:
#         degreeDict[d.split(',')[0]] = d.split(',')[1]
#     senWord = defaultdict()
#     notWord = defaultdict()
#     degreeWord = defaultdict()
#
#     for word in wordDict.keys():
#         if word in senDict.keys() and word not in notList and word not in degreeDict.keys():
#             senWord[wordDict[word]] = senDict[word]
#         elif word in notList and word not in degreeDict.keys():
#             notWord[wordDict[word]] = -1
#         elif word in degreeDict.keys():
#             degreeWord[wordDict[word]] = degreeDict[word]
#     return senWord, notWord, degreeWord


def classify_words(word_dict):
    """词语分类,找出情感词、否定词、程度副词"""
    # 读取情感字典文件
    sen_file = open('D:/Desktop/Desktop/GraduationDesign/BosonNLP_sentiment_score.txt', 'r+', encoding='utf-8')
    # 获取字典文件内容
    sen_list = sen_file.readlines()
    # 创建情感字典
    sen_dict = defaultdict()
    # 读取字典文件每一行内容，将其转换为字典对象，key为情感词，value为对应的分值
    for s in sen_list:
        # 每一行内容根据空格分割，索引0是情感词，索引01是情感分值
        sen_dict[s.split(' ')[0]] = s.split(' ')[1]

    # 读取否定词文件
    not_word_file = open('D:/Desktop/Desktop/GraduationDesign/notDict.txt', 'r+', encoding='utf-8')
    # 由于否定词只有词，没有分值，使用list即可
    not_word_list = not_word_file.readlines()

    # 读取程度副词文件
    degree_file = open('D:/Desktop/Desktop/GraduationDesign/degreeDict.txt', 'r+', encoding='utf-8')
    degree_list = degree_file.readlines()
    degree_dic = defaultdict()
    # 程度副词与情感词处理方式一样，转为程度副词字典对象，key为程度副词，value为对应的程度值
    for d in degree_list:
        degree_dic[d.split(',')[0]] = d.split(',')[1]

    # 分类结果，词语的index作为key,词语的分值作为value，否定词分值设为-1
    sen_word = dict()
    not_word = dict()
    degree_word = dict()

    # 分类
    for word in word_dict.keys():
        if word in sen_dict.keys() and word not in not_word_list and word not in degree_dic.keys():
            # 找出分词结果中在情感字典中的词
            sen_word[word_dict[word]] = sen_dict[word]
        elif word in not_word_list and word not in degree_dic.keys():
            # 分词结果中在否定词列表中的词
            not_word[word_dict[word]] = -1
        elif word in degree_dic.keys():
            # 分词结果中在程度副词中的词
            degree_word[word_dict[word]] = degree_dic[word]
    sen_file.close()
    degree_file.close()
    not_word_file.close()
    # 将分类结果返回
    return sen_word, not_word, degree_word


def list_to_dict(word_list):
    """将分词后的列表转为字典，key为单词，value为单词在列表中的索引，索引相当于词语在文档中出现的位置"""
    data = {}
    for x in range(0, len(word_list)):
        data[word_list[x]] = x
    return data


def get_init_weight(sen_word, not_word, degree_word):
    # 权重初始化为1
    W = 1
    # 将情感字典的key转为list
    sen_word_index_list = list(sen_word.keys())
    if len(sen_word_index_list) == 0:
        return W
    # 获取第一个情感词的下标，遍历从0到此位置之间的所有词，找出程度词和否定词
    for i in range(0, sen_word_index_list[0]):
        if i in not_word.keys():
            W *= -1
        elif i in degree_word.keys():
            # 更新权重，如果有程度副词，分值乘以程度副词的程度分值
            W *= float(degree_word[i])
    return W


def socre_sentiment(sen_word, not_word, degree_word, seg_result):
    """计算得分"""
    # 权重初始化为1
    W = 1
    score = 0
    # 情感词下标初始化
    sentiment_index = -1
    # 情感词的位置下标集合
    sentiment_index_list = list(sen_word.keys())
    # 遍历分词结果(遍历分词结果是为了定位两个情感词之间的程度副词和否定词)
    for i in range(0, len(seg_result)):
        # 如果是情感词（根据下标是否在情感词分类结果中判断）
        if i in sen_word.keys():
            # 权重*情感词得分
            score += W * float(sen_word[i])
            # 情感词下标加1，获取下一个情感词的位置
            sentiment_index += 1
            if sentiment_index < len(sentiment_index_list) - 1:
                # 判断当前的情感词与下一个情感词之间是否有程度副词或否定词
                for j in range(sentiment_index_list[sentiment_index], sentiment_index_list[sentiment_index + 1]):
                    # 更新权重，如果有否定词，取反
                    if j in not_word.keys():
                        W *= -1
                    elif j in degree_word.keys():
                        # 更新权重，如果有程度副词，分值乘以程度副词的程度分值
                        W *= float(degree_word[j])
        # 定位到下一个情感词
        if sentiment_index < len(sentiment_index_list) - 1:
            i = sentiment_index_list[sentiment_index + 1]
    return score


# 计算得分
def setiment_score(sententce):
    # 1.对文档分词
    seg_list = seg_word(sententce)
    # 2.将分词结果列表转为dic，然后找出情感词、否定词、程度副词
    sen_word, not_word, degree_word = classify_words(list_to_dict(seg_list))
    # 3.计算得分
    score = socre_sentiment(sen_word, not_word, degree_word, seg_list)
    return score


# 测试
if __name__ == '__main__':
    # weiboId = '4367825973874268'
    weiboId = str(argv[1])
    # RF = joblib.load('D:/Desktop/Desktop/GraduationDesign/rf.model')   #加载模型
    # print('加载模型成功')
    # df_analyser = pd.DataFrame(columns=['comment', 'sentiment'])
    connect_info = 'mysql+pymysql://root:password@localhost:3306/textanalyser'
    sql_cmd = "SELECT id,comments from comment_info where weiboId="+weiboId
    engine = create_engine(connect_info)

    df = pd.read_sql(sql=sql_cmd, con=engine)
    idSet = df.id
    result_y = []

    #使用情感词典方法进行训练
    for index, row in df.iterrows():
        result = setiment_score(row.comments)
        result_y.append(result)


    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='textanalyser')
    conn.autocommit(True)
    cur = conn.cursor()
#将分析后的情感写入数据库
    for i in range(len(idSet)):
        sql_update ='UPDATE comment_info SET sentiment={} where id ={};'.format(result_y[i],idSet[i])
        cur.execute(sql_update)
    sql_update_status = "update analyseresult set status='yes' where weiboId='"+weiboId+"'"
    cur.execute(sql_update_status)


    # 形成男女比例对比图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='textanalyser')
    # conn.autocommit(True)
    # cur = conn.cursor()

    sql_male_pos = "select count(*) from comment_info where userGender='m' and sentiment>=0 and weiboId='" + weiboId + "'"
    cur.execute(sql_male_pos)
    male_pos = cur.fetchone()[0]

    sql_male_neg = "select count(*) from comment_info where userGender='m' and sentiment<0 and weiboId='" + weiboId + "'"
    cur.execute(sql_male_neg)
    male_neg = cur.fetchone()[0]

    sql_female_pos = "select count(*) from comment_info where userGender='f' and sentiment>=0 and weiboId='" + weiboId + "'"
    cur.execute(sql_female_pos)
    female_pos = cur.fetchone()[0]

    sql_female_neg = "select count(*) from comment_info where userGender='f' and sentiment<0 and weiboId='" + weiboId + "'"
    cur.execute(sql_female_neg)
    female_neg = cur.fetchone()[0]

    cur.close()
    conn.close()

    ## 使用matplotlib制作饼图
    labels = ['男积极', '男消极', '女积极', '女消极']
    data = [male_pos, male_neg, female_neg, female_pos]
    plt.pie(data, labels=labels, autopct='%1.2f%%')
    plt.axis('equal')

    # plt.legend(loc = 'center left')
    plt.title("男女比例对比饼图", loc='left')
    print("okokok")
    plt.savefig("D:/desktop/desktop/TextAnalyser/src/main/webapp/images/dataVisualization/" + weiboId + "_fm.jpg")
    print("okokok")





