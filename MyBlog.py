import re
from flask import Flask, render_template, url_for, request, redirect, make_response, session
import os
import MySQLdb
import User
import datetime


app = Flask(__name__)
app.secret_key = "abcde"

image_path = os.path.join(os.getcwd(), "static/images")


@app.route("/")
def to_index():
    return redirect("/index")
    # return render_template("writer.html")


@app.route('/index')
def index():
    "获取首页所需数据"
    # 基础连接信息
    islogin = session.get("is_login")
    cookies_uid = request.cookies.get("uid")
    conn = MySQLdb.connect(user="root", password="root", host="localhost", charset="utf8")
    conn.select_db("blog")
    curr = conn.cursor()

    # 获取导航栏项
    curr.execute("SELECT id,navname FROM nav_t")
    conn.commit()
    results = curr.fetchall()
    nav_list = []
    for row in results:
        nav_list.append(row[1])

    # 获取博客文章信息
    target_page_get = request.args.get("target_page")
    if target_page_get is None or len(target_page_get) <= 0:
        target_page = 1
    else:
        target_page = int(target_page_get)
    start_page = (target_page-1)*10
    curr.execute("SELECT id,title,content,imgpath,readings,createdate,tags,description FROM article_t ORDER BY id DESC LIMIT %s,%s", (start_page, 10))
    conn.commit()
    results = curr.fetchall()
    blog_list = []
    for row in results:
        blog = {}
        blog["id"] = row[0]
        blog["title"] = row[1]
        blog["content"] = row[2]
        if len(row[3]) > 0 and row[3] is not None:
            imgurl = "images/%s" % row[3]
            blog["imgpath"] = url_for("static", filename=imgurl)
        else:
            blog["imgpath"] = ""
        blog["readings"] = row[4]
        blog["createdate"] = row[5]
        blog["tags"] = row[6]
        blog["description"] = row[7]
        blog_list.append(blog)

    # 获取文章的总数
    curr.execute("SELECT COUNT(id) FROM article_t")
    conn.commit()
    results = curr.fetchall()
    blog_size = results[0][0]

    # 获取轮播文章
    curr.execute("SELECT id,title,imgpath FROM article_t WHERE imgpath <> '' ORDER BY readings DESC LIMIT 4")
    conn.commit()
    results = curr.fetchall()
    carousel_list = []
    for row in results:
        carousel = {}
        carousel["id"] = row[0]
        carousel["title"] = row[1]
        imgurl = "images/%s" % row[2]
        carousel["imgpath"] = url_for("static", filename=imgurl)
        carousel_list.append(carousel)

    # 获取标签项
    curr.execute("SELECT id,tag FROM tag_t")
    conn.commit()
    results = curr.fetchall()
    tag_list = []
    for row in results:
        tag = {}
        tag["id"] = row[0]
        tag["name"] = row[1]
        tag_list.append(tag)

    # 获取热门文章
    curr.execute("SELECT id,title FROM article_t ORDER BY readings DESC LIMIT 10")
    conn.commit()
    results = curr.fetchall()
    hot_list = []
    for row in results:
        hot = {}
        hot["id"] = row[0]
        hot["title"] = row[1]
        hot_list.append(hot)

    # 获取用户信息
    if not cookies_uid:
        loginusername = ""
        userimg = url_for("static", filename="images/unknownuser.png")
        userinfo = None
    else:
        curr.execute("SELECT id,username,realname,imgpath,access,description FROM user_t WHERE id = %s", cookies_uid)
        conn.commit()
        results = curr.fetchall()
        userinfo = User.User()
        userinfo.uid = cookies_uid
        userinfo.username = results[0][1]
        userinfo.realname = results[0][2]
        userinfo.imgpath = results[0][3]
        if len(userinfo.imgpath) <= 0:
            userinfo.imgpath = "unknownuser.png"
        userinfo.access = results[0][4]
        userinfo.description = results[0][5]
        loginusername = userinfo.realname
        session["loginusername"] = loginusername
        imgurl = "images/%s" % userinfo.imgpath
        userimg = url_for("static", filename=imgurl)
        session["userimg"] = userimg

    # 返回数据
    return render_template("index.html", nav_list=nav_list, loginusername=loginusername, userimg=userimg,
                           userinfo=userinfo, blog=blog_list, blogtag=tag_list, blogsize=blog_size, islogin=islogin,
                           carousel_list=carousel_list, hot_list=hot_list, target_page=target_page)


@app.route("/content")
def content():
    "获取文章页内容"
    islogin = session.get("is_login")
    cookies_uid = request.cookies.get("uid")
    article_id = request.args.get("ai")
    conn = MySQLdb.connect(user="root", password="root", host="localhost", charset="utf8")
    conn.select_db("blog")
    curr = conn.cursor()
    curr.execute("SELECT id,title,content,imgpath,readings,createdate,tags,description FROM article_t WHERE id = %s", article_id)
    conn.commit()
    results = curr.fetchall()
    blog = {}
    blog["id"] = results[0][0]
    blog["title"] = results[0][1]
    blog["content"] = results[0][2]
    blog["imgpath"] = results[0][3]
    blog["readings"] = results[0][4]
    blog["createdate"] = results[0][5]
    blog["tags"] = results[0][6]
    blog["description"] = results[0][7]
    curr.execute("SELECT id,tag FROM tag_t WHERE id IN (%s)", blog["tags"])
    conn.commit()
    results = curr.fetchall()
    a_tag_list = []
    for row in results:
        a_tag = {}
        a_tag["id"] = row[0]
        a_tag["tag"] = row[1]
        a_tag_list.append(a_tag)


    # 获取导航栏项
    curr.execute("SELECT id,navname FROM nav_t")
    conn.commit()
    results = curr.fetchall()
    nav_list = []
    for row in results:
        nav_list.append(row[1])

    # 获取标签项
    curr.execute("SELECT id,tag FROM tag_t")
    conn.commit()
    results = curr.fetchall()
    tag_list = []
    for row in results:
        tag = {}
        tag["id"] = row[0]
        tag["name"] = row[1]
        tag_list.append(tag)

    # 获取热门文章
    curr.execute("SELECT id,title FROM article_t ORDER BY readings DESC LIMIT 10")
    conn.commit()
    results = curr.fetchall()
    hot_list = []
    for row in results:
        hot = {}
        hot["id"] = row[0]
        hot["title"] = row[1]
        hot_list.append(hot)

    # 获取用户信息
    if not cookies_uid:
        loginusername = ""
        userimg = url_for("static", filename="images/unknownuser.png")
        userinfo = None
    else:
        curr.execute("SELECT id,username,realname,imgpath,access,description FROM user_t WHERE id = %s", cookies_uid)
        conn.commit()
        results = curr.fetchall()
        userinfo = User.User()
        userinfo.uid = cookies_uid
        userinfo.username = results[0][1]
        userinfo.realname = results[0][2]
        userinfo.imgpath = results[0][3]
        if len(userinfo.imgpath) <= 0:
            userinfo.imgpath = "unknownuser.png"
        userinfo.access = results[0][4]
        userinfo.description = results[0][5]
        loginusername = userinfo.realname
        imgurl = "images/%s" % userinfo.imgpath
        userimg = url_for("static", filename=imgurl)

    return render_template("content.html", a_tag_list=a_tag_list, tag_list=tag_list, blog=blog, nav_list=nav_list,
                           hot_list=hot_list, loginusername=loginusername, userimg=userimg, userinfo=userinfo, islogin=islogin)


def upload():
    "上传方法"
    if request.method == "POST":
        file = request.files.get("file")
        filesuffix = (file.filename.split("."))[-1]
        filename = str(datetime.datetime.now())
        reg = re.compile("\\W")
        filename = reg.sub("", filename)
        filename = filename + "." + filesuffix
        file.save(os.path.join("static/images", filename))
        return filename
    else:
        return ""


@app.route("/login", methods=["GET", "POST"])
def login():
    "登录方法"
    if request.method == "POST":
        username = request.form.get("username")
        if len(username) >= 0:
            pwd = request.form.get("pwd")
            conn = MySQLdb.connect(user="root", password="root", host="localhost", charset="utf8")
            conn.select_db("blog")
            curr = conn.cursor()
            curr.execute("SELECT id FROM user_t WHERE username=%s AND password=%s", (username, pwd))
            conn.commit()
            results = curr.fetchall()
            flag = False
            response = make_response(redirect("/index"))
            uid = results[0][0]
            if uid > 0:
                response.set_cookie("uid", value=str(uid))
                session["is_login"] = "1"
                flag = True
            else:
                session["is_login"] = "0"
            curr.close()
            conn.close()
            if flag:
                return response
            else:
                return render_template("login.html", username=username, tips="用户名或密码错误")
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    "登出方法"
    session["is_login"] = "0"
    response = make_response(redirect("/index"))
    response.delete_cookie("uid")
    return response


@app.route("/writer", methods=["GET", "POST"])
def writer():
    "文章编辑方法"
    islogin = session.get("is_login")
    if islogin == "1":
        loginusername = session.get("loginusername")
        userimg = session.get("userimg")
        add_article = request.form.get("add_article")
        if add_article == "1":
            art = request.form.get("content")
            print(art)
            response = make_response(redirect("/index"))
            return response
        else:
            conn = MySQLdb.connect(user="root", password="root", host="localhost", charset="utf8")
            conn.select_db("blog")
            curr = conn.cursor()
            # 获取标签项
            curr.execute("SELECT id,tag FROM tag_t")
            conn.commit()
            results = curr.fetchall()
            tag_list = []
            for row in results:
                tag = {}
                tag["id"] = row[0]
                tag["name"] = row[1]
                tag_list.append(tag)

            # 获取热门文章
            curr.execute("SELECT id,title FROM article_t ORDER BY readings DESC LIMIT 10")
            conn.commit()
            results = curr.fetchall()
            hot_list = []
            for row in results:
                hot = {}
                hot["id"] = row[0]
                hot["title"] = row[1]
                hot_list.append(hot)
            return render_template("writer.html", loginusername=loginusername, userimg=userimg, islogin=islogin,
                                   tag_list=tag_list, hot_list=hot_list)
    else:
        response = make_response(redirect("/index"))
        return response


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8086)
