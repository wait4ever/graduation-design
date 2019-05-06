import time
import base64
import rsa
import binascii
import requests
import re
from PIL import Image
import random
from urllib.parse import quote_plus
import http.cookiejar as cookielib
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sys import argv
import json
import datetime

agent = 'mozilla/5.0 (windowS NT 10.0; win64; x64) appLewEbkit/537.36 (KHTML, likE gecko) chrome/71.0.3578.98 safari/537.36'
headers = {'User-Agent': agent}

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

class WeiboLogin(object):
    """
    通过登录 weibo.com 然后跳转到 m.weibo.cn
    """
    #初始化数据
    def __init__(self, user, password, cookie_path):
        super(WeiboLogin, self).__init__()
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.cookie_path = cookie_path
        # LWPCookieJar是python中管理cookie的工具，可以将cookie保存到文件，或者在文件中读取cookie数据到程序
        self.session.cookies = cookielib.LWPCookieJar(filename=self.cookie_path)
        self.index_url = "http://weibo.com/login.php"
        self.session.get(self.index_url, headers=headers, timeout=2)
        self.postdata = dict()

    def get_su(self):
        """
        对 email 地址和手机号码 先 javascript 中 encodeURIComponent
        对应 Python 3 中的是 urllib.parse.quote_plus
        然后在 base64 加密后decode
        """
        username_quote = quote_plus(self.user)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    # 预登陆获得 servertime, nonce, pubkey, rsakv
    def get_server_data(self, su):
        """与原来的相比，微博的登录从 v1.4.18 升级到了 v1.4.19
        这里使用了 URL 拼接的方式，也可以用 Params 参数传递的方式
        """
        pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
        pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_="
        pre_url = pre_url + str(int(time.time() * 1000))
        pre_data_res = self.session.get(pre_url, headers=headers)
        # print("*"*50)
        # print(pre_data_res.text)
        # print("*" * 50)
        sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

        return sever_data

    def get_password(self, servertime, nonce, pubkey):
        """对密码进行 RSA 的加密"""
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)  # 拼接明文js加密文件中得到
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
        return passwd


    def get_cha(self, pcid):
        """获取验证码，并且用PIL打开，
        1. 如果本机安装了图片查看软件，也可以用 os.subprocess 的打开验证码
        2. 可以改写此函数接入打码平台。
        """
        cha_url = "https://login.sina.com.cn/cgi/pin.php?r="
        cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
        cha_url = cha_url + pcid
        cha_page = self.session.get(cha_url, headers=headers)
        with open("cha.jpg", 'wb') as f:
            f.write(cha_page.content)
            f.close()
        try:
            im = Image.open("cha.jpg")
            im.show()
            im.close()
        except Exception as e:
            print(u"请到当前目录下，找到验证码后输入")

    def pre_login(self):
        # su 是加密后的用户名
        su = self.get_su()
        sever_data = self.get_server_data(su)
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        rsakv = sever_data["rsakv"]
        pubkey = sever_data["pubkey"]
        showpin = sever_data["showpin"]  # 这个参数的意义待探索
        password_secret = self.get_password(servertime, nonce, pubkey)

        self.postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': "https://passport.weibo.com",
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': password_secret,
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '115',
            "cdult": "38",
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT'  # 这里是 TEXT 和 META 选择，具体含义待探索
        }
        return sever_data

    def login(self):
        # 先不输入验证码登录测试
        try:
            sever_data = self.pre_login()
           # print(sever_data)
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_'
            login_url = login_url + str(time.time() * 1000)
            login_page = self.session.post(login_url, data=self.postdata, headers=headers)
            ticket_js = login_page.json()
            ticket = ticket_js["ticket"]
        except Exception as e:
            sever_data = self.pre_login()  #先预登入
            #print(sever_data)
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_'
            login_url = login_url + str(time.time() * 1000)
            pcid = sever_data["pcid"]
            self.get_cha(pcid)
            self.postdata['door'] = input(u"请输入验证码")
            login_page = self.session.post(login_url, data=self.postdata, headers=headers)
            ticket_js = login_page.json()
            ticket = ticket_js["ticket"]
        # 以下内容是 处理登录跳转链接
        save_pa = r'==-(\d+)-'
        ssosavestate = int(re.findall(save_pa, ticket)[0]) + 3600 * 7
        jump_ticket_params = {
            "callback": "sinaSSOController.callbackLoginStatus",
            "ticket": ticket,
            "ssosavestate": str(ssosavestate),
            "client": "ssologin.js(v1.4.19)",
            "_": str(time.time() * 1000),
        }
        jump_url = "https://passport.weibo.com/wbsso/login"
        jump_headers = {
            "Host": "passport.weibo.com",
            "Referer": "https://weibo.com/",
            "User-Agent": headers["User-Agent"]
        }
        jump_login = self.session.get(jump_url, params=jump_ticket_params, headers=jump_headers)
        uuid = jump_login.text

        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
        web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
        weibo_page = self.session.get(web_weibo_url, headers=headers)

        # print(weibo_page.content.decode("utf-8")

        Mheaders = {
            "Host": "login.sina.com.cn",
            "User-Agent": agent
        }

        # m.weibo.cn 登录的 url 拼接
        _rand = str(time.time())
        mParams = {
            "url": "https://m.weibo.cn/",
            "_rand": _rand,
            "gateway": "1",
            "service": "sinawap",
            "entry": "sinawap",
            "useticket": "1",
            "returntype": "META",
            "sudaref": "",
            "_client_version": "0.6.26",
        }
        murl = "https://login.sina.com.cn/sso/login.php"
        mhtml = self.session.get(murl, params=mParams, headers=Mheaders)
        mhtml.encoding = mhtml.apparent_encoding
        mpa = r'replace\((.*?)\);'
        mres = re.findall(mpa, mhtml.text)

        # 关键的跳转步骤，这里不出问题，基本就成功了。
        Mheaders["Host"] = "passport.weibo.cn"
        self.session.get(eval(mres[0]), headers=Mheaders)
        mlogin = self.session.get(eval(mres[0]), headers=Mheaders)
        # print(mlogin.status_code)
        # 进过几次 页面跳转后，m.weibo.cn 登录成功，下次测试是否登录成功
        Mheaders["Host"] = "m.weibo.cn"
        Set_url = "https://m.weibo.cn"
        pro = self.session.get(Set_url, headers=Mheaders)
        pa_login = r'isLogin":true,'
        login_res = re.findall(pa_login, pro.text)
        # print(login_res)

        # 可以通过 session.cookies 对 cookies 进行下一步相关操作
        self.session.cookies.save()
        # print("*"*50)
        # print(self.cookie_path)

def weibo_comment(id):
    max_id = ""
    headers = {"user-agent": "mozilla/5.0 (windowS NT 10.0; win64; x64) appLewEbkit/537.36 (KHTML, likE gecko) chrome/71.0.3578.98 safari/537.36"}
    #加载cookie
    cookies = cookielib.LWPCookieJar("Cookie.txt")
    cookies.load(ignore_discard=True, ignore_expires=True)
    # 将cookie转换成字典
    cookie_dict = requests.utils.dict_from_cookiejar(cookies)
    #读入语料csv文件
    df_empty = pd.DataFrame(columns=['weiboId', 'userName', 'userGender', 'comments'])
    index = 1
    while True:
        if max_id == "":
            url = "https://m.weibo.cn/comments/hotflow?id="+id+"&mid="+id+"&max_id_type=0"
        else:
            url = "https://m.weibo.cn/comments/hotflow?id="+id+"&mid="+id+"&max_id="+str(max_id)+"&max_id_type=0"
        # print(url)
        response = requests.get(url, headers=headers, cookies=cookie_dict)
        # print(response.text)
        try:
            comment = response.json()
        except Exception as e:
            return "error"

        if comment['ok'] == 0:
            break
        max_id = comment["data"]["max_id"]

        for comment_data in comment["data"]["data"]:
            data = comment_data["text"]
            p = re.compile(r'(<span.*>.*</span>)*(<a.*>.*</ a>)?')
            data = p.sub(r'', data)
            # 过滤@..
            label_filter = re.compile(r'<a.*</a>\s*', re.S)
            data = label_filter.sub(r'', data)
            # 过滤掉空评论
            if (data.strip() == ''):
                continue

            user = comment_data["user"]["screen_name"]
            gender = comment_data["user"]["gender"]
            add_data = pd.Series({'weiboId': id, 'userName': user, 'userGender': gender, 'comments': data})
            df_empty = df_empty.append(add_data, ignore_index=True)
        if(max_id == 0):
            break
        index = index+1
        time.sleep(1+random.randint(1, 3))
    print("成功抓取" + str(index) + "页评论内容")
    #连接数据库 将数据存入数据库
    connect_info = 'mysql+pymysql://root:password@localhost:3306/textanalyser'
    con = create_engine(connect_info)
    pd.io.sql.to_sql(df_empty, 'comment_info', con, schema='textanalyser', if_exists='append', index=False)



    # df_empty.to_csv('D:/Desktop/Desktop/GraduationDesign/weiboComment.csv', encoding='utf_8_sig', index=False)
    # i = 1
    # count =100
    # head_url = "https://m.weibo.cn/api/comments/show?id=4176281144304232&page="
    # fp = open("奚梦瑶.txt", "a", encoding="utf8")
    #
    # while i <= count:
    #     # try:
    #     url = head_url + str(i)
    #     resp = requests.get(url)
    #     resp.encoding = resp.apparent_encoding
    #     print(resp.text)
    #     comment_json = json.loads(resp.text)
    #     comments_list = comment_json["data"]["data"]
    #     for commment_item in comments_list:
    #         username = commment_item["user"]["screen_name"]
    #         comment = commment_item["text"]
    #         label_filter = re.compile(r'</?\w+[^>]*>', re.S)
    #         comment = re.sub(label_filter, '', comment)
    #         fp.write(comment)
    #     print(i)
    #     # except Exception as e:
    #     #     print(e)
    #     #     continue
    #     i += 1
    # fp.close()

if __name__ == '__main__':
    username = "272451865@qq.com"  # 用户名
    password = "ljmpeak0419"  # 密码
    cookie_path = "Cookie.txt"  # 保存cookie 的文件名称
    weibo = WeiboLogin(username, password, cookie_path)
    weibo.login()
    # id='4367977325433800'
    id = argv[1]
    createdTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    info = weibo_comment(id)
    if(info=="error"):
        print("微博ID错误，请重新输入！")
    else:
        #存入数据
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='textanalyser')
        conn.autocommit(True)
        cur = conn.cursor()
        sql_insert = "insert into analyseresult values('"+id+"','no','"+createdTime+"')"
        print(sql_insert)
        cur.execute(sql_insert)

        print("微博信息爬取完成，请等待分析结果。")
