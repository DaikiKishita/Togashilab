from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sq
import time
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from matplotlib.font_manager import FontProperties
import json
from urllib.request import Request, urlopen
import numpy as np
import math
import japanize_matplotlib
import matplotlib.pyplot as plt
from flask_apscheduler import APScheduler
import datetime

under_word=["少し滞在時間が短くないか？","君の滞在時間はもっと伸びるよ！","まだまだ滞在時間が短いな","滞在時間もっと増やしたいと思わないのかい？","あんたの滞在時間なんて気にしてないんだから！"]
middle_word=["まあまあかな","その調子よ！","その調子だ！","君のその滞在時間が俺に力を与えるんだ！","もっと！もっとだ！","まあまあいたね！"]
top_word=["君は立派な富樫研人だ！","富樫研に住所変更した？","富樫研大好きじゃん","もう研究室に囚われてるよ","研究で忙しいんだね.."]

app = Flask(__name__,static_folder='./templates/images')
scheduler = APScheduler()
app.config['SCHEDULER_API_ENABLED'] = True
scheduler.init_app(app)

from apscheduler.triggers.cron import CronTrigger

dbname = "static/Users.db"
IMG_DIR="templates/images/graph.jpg"
webhook_url = 'https://discord.com/api/webhooks/1133949849214132295/72NtKPm2YUCpinJYSw7ecoobW0n-l-0Sop9ZEppqQdZCETY-hbk4t04Nu8PN_WIRstJ-'
name_dic=dict()
OTP=0


#データベースで時間を計算するのがとても面倒だったために作られた関数
class Times:
    def __init__(self,name):
        self.name=name
        self.timer=0
        self.Stimer=0
    
    def In(self,s):
        self.Stimer=s
    
    def Out(self,e):
        if self.timer==0:
            self.timer=e-self.Stimer
        else:
            self.timer+=e-self.Stimer
        return e-self.Stimer
    
    def TempOut(self,t):
        self.timer+=t-self.Stimer
        return t-self.Stimer
    
    def FTempOut(self,t):
        self.timer=t-self.Stimer
        return t-self.Stimer
    
    def TempIn(self,r):
        self.timer-=r

#名前の長さを統一する為の関数
def arrange_name(name:str):
    if len(name) < 4:
        add_space=4-len(name)
        name+="　"*add_space
    elif len(name)>4:
        str_lst=list(name)[0:4]
        name=""
        for i in str_lst:
            name+=i
    return name.replace(" ","　")

#富樫研discordserverへ入退室の状況を送る為の関数
def post_discord(message: str, webhook_url: str):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (private use) Python-urllib/3.10",
    }
    data = {"content": message}
    request = Request(
        webhook_url,
        data=json.dumps(data).encode(),
        headers=headers,
    )

    with urlopen(request) as res:
        assert res.getcode() == 204

#時間表記を分かりやすくする為の関数
def make_time(r):
    string=""
    if r == None:
        return "0秒"
    else:
        if r>=3600:
            hour=math.floor(r//3600)
            r=r%3600
            string+=f"{hour}時間"
        if r>=60:
            minute=math.floor(r//60)
            r=r%60
            string+=f"{minute}分"
        seconds=math.floor(r//1)
        string+=f"{seconds}秒"
        return string

#データベースへSQLを打つための関数
def exesql(sql,tex):
    with sq.connect(dbname) as conn:
        cur = conn.cursor()
        if tex=="":
            result = cur.execute(sql)
            conn.commit()
            if result is None:
                return []
            return list(result)
        else:
            cur.execute(sql,tex)
            conn.commit()

#webapp起動時のデータベースからのデータの移し,バックアップ
result=exesql("select name,timer from Users","")
if result != []:
    for i in result:
        name_dic[i[0]]=Times(i[0])
        try:
            name_dic[i[0]].timer=i[1]
        except:
            continue

exesql("update Users set color='silver'","")#入館システム起動時の全員の入館情報の色の初期化

#404エラーへの対処
@app.errorhandler(404)
def error_404(error):
    return render_template("404.html")

@app.route("/", methods=["GET", "POST"])
def index():
    cnt=4
    if request.method == "POST":
        t=time.time()
        names=request.form["user"]
        color=exesql(f"select color from Users where name='{names}'","")[0][0]
        if color=="green":
            r=name_dic[f"{names}"].Out(t)
            exesql(f"update Users set color='red',timer='{name_dic[f'{names}'].timer}' where name='{names}'","")
            string=""
            if r<=3600*5:
                string=under_word[np.random.randint(0,len(under_word))]
            elif r<=3600*12:
                string=middle_word[np.random.randint(0,len(middle_word))]
            else:
                string=top_word[np.random.randint(0,len(top_word))]
            post_discord(f'{names}が退室しました\n\t\t滞在時間:{make_time(r)}\n{string}\n', webhook_url)
        else:
            name_dic[f"{names}"].In(t)
            exesql(f"update Users set color='green' where name='{names}'","")
            post_discord(f"{names}が入室しました\n",webhook_url)
    result = exesql("select name,color from Users","")
    text = "<table border='0' style='margin:auto'><tr>"
    width="300"
    height="300"
    cnts=1
    for i in result:
        text += f"<form action='/' method='POST'><td><input type='hidden' name='user' value='{i[0]}'><input type='submit' value='{arrange_name(i[0])}' style='background-color:{i[1]}; font-size: 400%; border: 0px; width={width}; height={height}'></td></form>"
        if cnts>=cnt:
            text+="</tr><tr>"
            cnt+=4
        cnts+=1
    text+="</tr></table>"
    return render_template("index.html", info=text)

@app.route("/input",methods=["GET","POST"])
def input_date():
    if request.method=="POST":
        name=request.form["name"]
        sql = "INSERT INTO Users (name, color) VALUES ( ?, ?)"
        exesql(sql, (name, 'silver'))
        name_dic[f"{name}"]=Times(name)
        return redirect(url_for("index"))
    else:
        return render_template("input.html")

@app.route("/detail",methods=["GET","POST"])
def delete():
    result=exesql("select name from Users","")
    return render_template("detail.html", names=result)

@app.route("/graph",methods=["GET"])
def graph():
    names=exesql("select name from Users where color=\"green\"","")
    t=time.time()
    for i in names:
        if name_dic[f"{i[0]}"].timer!=None:
            r=name_dic[f"{i[0]}"].TempOut(t)
        else:
            r=name_dic[f"{i[0]}"].FTempOut(t)
        exesql(f"update Users set timer='{name_dic[f'{i[0]}'].timer}' where name='{i[0]}'","")
        name_dic[f"{i[0]}"].TempIn(r)
    
    name=[]
    times=[]
    for i in name_dic:
        if name_dic[i].timer!=None:
            name.append(i)
            times.append(name_dic[i].timer//3600)
    fig=plt.figure()
    sns.barplot(x=name, y=times)
    plt.title(u"在室時間")
    line_plot = sns.lineplot()
    figure = line_plot.get_figure()
    figure.savefig(IMG_DIR)
    timers=exesql("select timer from (select Rank() OVER(ORDER BY timer DESC) as ranking,name,timer from Users) where ranking<=3 order by ranking","")
    timer=[make_time(i[0]) for i in timers]
    ranking=exesql("select ranking,name from (select Rank() OVER(ORDER BY timer DESC) as ranking,name from Users) where ranking<=3 order by ranking","")
    return render_template("graph.html",ranking=ranking,timer=timer,lens=len(ranking))

@app.route("/delete",methods=["GET","POST"])
def send_data():
    global OTP
    if request.method=="POST":
        password=request.form["password"]
        if password==str(OTP):
            name=request.form["name"]
            exesql(f"delete from Users where name='{name}'","")
            return redirect(url_for("index"))
        else:
            return render_template("delete.html",result="OTPの値が違います")
    else:
        OTP=np.random.randint(100000,999999)
        print("OTP:",OTP)
        return render_template("delete.html",example="OTPを入力してください")


def my_job():
    now=datetime.datetime.now()
    for i in name_dic.keys():
        exesql("insert into Monthliy (name, maxtimer,Year,Month) VALUES ( ?, ?)",(name_dic[i].name,name_dic[i].timer,now.year,now.month))
        exesql(f"update Monthliy set timer='0' where name={i}","")
        name_dic[i].timer=0

scheduler.add_job(
    id='my_job_id',
    func=my_job,
    trigger=CronTrigger(day='last'), # 月末を指定
    replace_existing=True
)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
