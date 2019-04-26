import pandas as pd
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn import metrics
from sklearn.externals import joblib
from sklearn.linear_model import SGDClassifier
from snownlp import SnowNLP
def get_sentiment(text):
    return SnowNLP(text).sentiments

def chinese_word_cut(mytext):
    return " ".join(jieba.cut(mytext))

def get_custom_stopwords(stop_words_file):
    with open(stop_words_file) as f:
        stopwords = f.read()
    stopwords_list = stopwords.split('\n')
    custom_stopwords_list = [i for i in stopwords_list]
    return custom_stopwords_list

# 读取语料库
df = pd.read_csv(r"dataset_small3000.csv",encoding='gbk')  #gbk
# X为评论
X = df[['comment']].astype(str)
# 对评论进行分词
X['cut_comment'] = X.comment.apply(chinese_word_cut)
# y为情感 0-消极 1-积极
y = df.sentiment
# 读取停用词表（哈工大）
stop_words_file = "stopwordsHIT.txt"
stopwords = get_custom_stopwords(stop_words_file)
max_df = 0.8  # 在超过这一比例的文档中出现的关键词（过于平凡），去除掉。
min_df = 3  # 在低于这一数量的文档中出现的关键词（过于独特），去除掉。

#拆分训练集、测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

vect = CountVectorizer(max_df=max_df,
                       min_df=min_df,
                       token_pattern=u'(?u)\\b[^\\d\\W]\\w+\\b',
                       stop_words=frozenset(stopwords))
term_matrix = pd.DataFrame(vect.fit_transform(X.cut_comment).toarray(), columns=vect.get_feature_names())
# print(term_matrix)
# term_matrix.to_csv("term.csv",encoding="utf-8")
nb = MultinomialNB()
sdg =SGDClassifier()
pipe = make_pipeline(vect, nb)
value = cross_val_score(pipe, X_train.cut_comment, y_train, cv=5, scoring='accuracy').mean()

rf = pipe.fit(X_train.cut_comment, y_train) #拟合出模型
y_pred = pipe.predict(X_test.cut_comment)  #测试集测试

print(type(X_test.cut_comment))


#输入
df_test1 = pd.read_csv(r"a.csv",encoding='gbk')  #gbk
y_pred = pipe.predict(df_test1['comments'].astype(str))
df_test1['sentiment']=y_pred
df_test1.to_csv("a.csv")

#将测试集正确结果与预测结果输出成.csv文件，人工做比对，看哪句被判断错误
# df_result = pd.DataFrame(columns=['comment', 'right_sentiment', 'pre_sentiment'])
# df_result['comment'] = X_test.cut_comment
# df_result['right_sentiment'] = y_test
# df_result['pre_sentiment'] = y_pred
# df_result.to_csv("result.csv",encoding="utf-8")



# print(y_test)
# for i in range(len(X_test.cut_comment)):
#     print(X_test.cut_comment[i])


print("测试集预测准确率： "+metrics.accuracy_score(y_test, y_pred))
print(metrics.confusion_matrix(y_test, y_pred))

# 调用SnowNLP库进行情感预测试试。 只有60.2%准确率
# y_pred_snownlp = X_test.comment.apply(get_sentiment)
# y_pred_snownlp_normalized = y_pred_snownlp.apply(lambda x: 1 if x>0.5 else 0)
# print(metrics.accuracy_score(y_test, y_pred_snownlp_normalized))

# joblib.dump(rf,'rf.model')   #保存模型
# RF=joblib.load('rf.model')   #加载模型

# print(RF.predict(X_test.cut_comment))