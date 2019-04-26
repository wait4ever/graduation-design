import pandas as pd
import re

def data_preprocess(text):
    label_filter = re.compile(r'//@.*', re.S)  #去除转发回复
    label_filter2 = re.compile(r'@\w+', re.S)  #去除@...
    text = re.sub(label_filter, '',text)
    text = re.sub(label_filter2, '', text)
    return text


dataset = pd.DataFrame(columns=['comment', 'sentiment'])
print("正在进行格式化")
index = 0
with open("neg.txt") as f:
    for line in f.readlines():
        line = data_preprocess(line)
        add_data = pd.Series({'comment': line, 'sentiment': 0})
        dataset = dataset.append(add_data, ignore_index=True)
        index = index+1
        if index == 3000:
            index = 0
            break
        print ("已完成 "+str(index*100/120000)+"%")


with open("pos.txt") as f:
    for line in f.readlines():
        line = data_preprocess(line)
        add_data = pd.Series({'comment': line, 'sentiment': 1})
        dataset = dataset.append(add_data, ignore_index=True)
        index = index + 1
        if index == 3000:
            index = 0
            break
        print("已完成 " + str(index * 100 / 120000) + "%")

dataset.to_csv('dataset_small3000.csv', encoding='utf_8_sig', index=False)
print("格式化完成")

