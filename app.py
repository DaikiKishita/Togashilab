from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sq
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns

# 日本語フォントの設定
plt.rcParams['font.family'] = 'MS Gothic'

app = Flask(__name__,static_folder='./templates/images')
dbname = "static/Users.db"
IMG_DIR="templates/images/graph.jpg"
name_dic=dict()

class Times:
    def __init__(self,name):
        self.name=name
        self.timer=None
        self.Stimer=None
    
    def In(self,s):
        self.Stimer=s
    
    def Out(self,e):
        if self.timer==None:
            self.timer=e-self.Stimer
        else:
            self.timer+=e-self.Stimer
        return e-self.Stimer


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

result=exesql("select name,timer from Users","")
if result != []:
    for i in result:
        name_dic[i[0]]=Times(i[0])
        try:
            name_dic[i[0]].timer=i[1]
        except:
            continue
print("==========================================")
print("\t\t入館システム起動")
print("==========================================")
exesql("update Users set color='silver'","")#入館システム起動時の全員の入館情報の初期か

@app.route("/", methods=["GET", "POST"])
def index():
    text_len=1200
    if request.method == "POST":
        t=time.time()
        names=request.form["user"]
        color=exesql(f"select color from Users where name='{names}'","")[0][0]
        if color=="green":
            r=name_dic[f"{names}"].Out(t)
            exesql(f"update Users set color='red',timer='{name_dic[f'{names}'].timer}' where name='{names}'","")
            print(f"=========================================================================")
            print(f"\t\t{names}が退室しました\n\t\t滞在した時間:{r}")
            print("==========================================================================")
        else:
            name_dic[f"{names}"].In(t)
            exesql(f"update Users set color='green' where name='{names}'","")
            print("==========================================================================")
            print(f"\t\t{names}が入研しました")
            print("==========================================================================")
    result = exesql("select name,color from Users","")
    text = "<table border='0' style='margin:auto'><tr>"
    width="300"
    height="300"
    for i in result:
        text += f"<form action='/' method='POST'><td><input type='hidden' name='user' value='{i[0]}'><input type='submit' value='{i[0]}' style='background-color:{i[1]}; font-size: 250%; border: 0px; width={width}; height={height}'></td></form>"
        if len(text)>=text_len:
            text+="</tr><tr>"
            text_len+=text_len
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

@app.route("/delete",methods=["GET","POST"])
def delete():
    if request.method=="POST":
        name=request.form["user"]
        exesql(f"delete from Users where name='{name}'","")
        del name_dic[name]
    result=exesql("select name from Users","")
    return render_template("delete.html", names=result)

@app.route("/graph",methods=["GET"])
def graph():
    name=[]
    time=[]
    for i in name_dic:
        if name_dic[i].timer!=None:
            name.append(i)
            time.append(name_dic[i].timer)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    sns.barplot(x=name, y=time)
    plt.title("在室時間", fontname="MS Gothic")
    fig.savefig(IMG_DIR)
    return render_template("graph.html")

if __name__ == "__main__":
    app.run()
