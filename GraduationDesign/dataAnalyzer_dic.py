import pandas as pd
from sklearn.externals import joblib
from sqlalchemy import create_engine
import pymysql
from sys import argv
import trainModel_dic

if __name__ == '__main__':
    # weiboId = '4365345747167719'
    weiboId = str(argv[1])
    # RF = joblib.load('D:/Desktop/Desktop/GraduationDesign/rf.model')   #加载模型
    # print('加载模型成功')
    # df_analyser = pd.DataFrame(columns=['comment', 'sentiment'])
    connect_info = 'mysql+pymysql://root:password@localhost:3306/textanalyser'
    sql_cmd = "SELECT id,comments from comment_info where weiboId="+weiboId
    engine = create_engine(connect_info)

    df = pd.read_sql(sql=sql_cmd, con=engine)
    idSet = df.id

    #使用机器学习方法进行训练
    # result_y = RF.predict(df.comments)
    # result_y = result_y.tolist()
    result_y = []

    #使用情感词典方法进行训练
    for index, row in df.iterrows():
        result = trainModel_dic.setiment_score(row.comments)
        print(row.comments,result)
        result_y.append(result)


    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='textanalyser')
    conn.autocommit(True)
    cur = conn.cursor()
#将分析后的情感写入数据库
    for i in range(len(idSet)):
        sql_update ='UPDATE comment_info SET sentiment={} where id ={};'.format(result_y[i],idSet[i])
        cur.execute(sql_update)
    cur.close()
    conn.close()
    print("数据分析完成！")

    # df['sentiment'] = X_test.cut_comment
    # df_result['right_sentiment'] = y_test
    # df_result['pre_sentiment'] = y_pred
    # df_result.to_csv("result.csv",encoding="utf-8")
    # print(df)

