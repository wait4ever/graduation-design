from sklearn.externals import joblib
import pandas as pd
import re
label_filter = re.compile(r'<a.*</a>\s*', re.S)
comment = re.sub(label_filter, '', "<a href='/n/zc_张_'>@zc_张_</a> 寡姐真的太好看了还有评论里大家都在找基无命 哈哈哈哈哈")
print(comment)



