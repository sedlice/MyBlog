#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
from flask import Flask, render_template, url_for, request, redirect, make_response, session
import os
import pymysql
import User
import datetime
import json
import util
from urllib import request as req
import psutil
import platform

__author__ = "pyx"


app = Flask(__name__)
app.secret_key = "abcde"
sqlHelper = {"user": "root", "pwd": "root", "host": "localhost", "charset": "utf8"}

image_path = os.path.join(os.getcwd(), "static/images")


@app.route("/")
def to_index():
    return redirect("/index")


@app.route('/index')
def index():
    "获取首页所需数据"
    # 基础连接信息
    islogin = session.get("is_login")
    cookies_uid = request.cookies.get("uid")
    conn = pymysql.connect(user=sqlHelper.get("user"), password=sqlHelper.get("pwd"), host=sqlHelper.get("host"),
                           charset=sqlHelper.get("charset"))
    conn.select_db("blog")
    curr = conn.cursor()

    # 储存访问记录
    ip = request.remote_addr
    now_ip = session.get("now_ip")
    if ip != now_ip:
        reqInfo = req.Request(url="http://ip.taobao.com/service/getIpInfo.php?ip=123.118.28.89")
        ipInfoJson = (req.urlopen(reqInfo)).read()
        ipInfo = json.loads(ipInfoJson)
        if ipInfo["code"] == 0:
            ipInfoDict = ipInfo["data"]
            ip_add = ipInfoDict["ip"]
            ip_p = ipInfoDict["region"]
            ip_c = ipInfoDict["city"]
            vt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            curr.execute("INSERT INTO guest_t(IPAddress,province,city,visitTime) VALUES (%s,%s,%s,%s)",
                         (ip_add, ip_p, ip_c, vt))
            session["now_ip"] = ip
            session["now_ip_id"] = conn.insert_id()
            conn.commit()
        else:
            vt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            curr.execute("INSERT INTO guest_t(IPAddress,province,city,visitTime) VALUES ('0.0.0.0','未知','未知',%s)",
                         (vt,))
            session["now_ip_id"] = conn.insert_id()
            conn.commit()

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
        curr.execute("SELECT id,username,realname,imgpath,access,description FROM user_t WHERE id = %s", (cookies_uid,))
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
    conn = pymysql.connect(user=sqlHelper.get("user"), password=sqlHelper.get("pwd"), host=sqlHelper.get("host"),
                           charset=sqlHelper.get("charset"))
    conn.select_db("blog")
    curr = conn.cursor()

    # 储存浏览记录
    now_ip_id = session.get("now_ip_id")
    vt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if now_ip_id is None:
        now_ip_id = 0
    curr.execute("INSERT INTO guest_article_t(gId,aId,visitTime) VALUES (%s,%s,%s)", (now_ip_id, article_id, vt))

    # 各获取文章的标签
    curr.execute("UPDATE article_t SET readings=(readings+1) WHERE id=%s", (article_id,))
    conn.commit()
    curr.execute("SELECT id,title,content,imgpath,readings,createdate,tags,description FROM article_t WHERE id = %s", (article_id,))
    conn.commit()
    results = curr.fetchall()
    blog = {}
    blog["id"] = results[0][0]
    blog["title"] = results[0][1]
    blog["content"] = results[0][2]
    blog["content"] = results[0][2]
    blog["imgpath"] = results[0][3]
    blog["readings"] = results[0][4]
    blog["createdate"] = results[0][5]
    blog["tags"] = results[0][6]
    tag_arr = (blog["tags"]).split(",")
    blog["description"] = results[0][7]
    a_tag_list = []
    for row in tag_arr:
        curr.execute("SELECT id,tag FROM tag_t WHERE id=%s", (int(row),))
        conn.commit()
        results = curr.fetchall()
        a_tag = {}
        a_tag["id"] = results[0][0]
        a_tag["tag"] = results[0][1]
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
        curr.execute("SELECT id,username,realname,imgpath,access,description FROM user_t WHERE id = %s", (cookies_uid,))
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


@app.route("/uploadImg", methods=["GET", "POST"])
def uploadimg():
    "文章图片上传方法"
    if request.method == "POST":
        file = request.files.get("imgFile")
        filesuffix = (file.filename.split("."))[-1]
        filename = str(datetime.datetime.now())
        reg = re.compile("\\W")
        filename = reg.sub("", filename)
        filename = filename + "." + filesuffix
        filename = os.path.join("static/images", filename)
        file.save(filename)
        res = {"errno": 0, "data": [filename]}
        return json.dumps(res)
    else:
        return ""


@app.route("/upload", methods=["GET", "POST"])
def upload():
    "封面图片上传"
    if request.method == "POST":
        file = request.files.get("file")
        filesuffix = (file.filename.split("."))[-1]
        filename = str(datetime.datetime.now())
        reg = re.compile("\\W")
        filename = reg.sub("", filename)
        filename = filename + "." + filesuffix
        file.save(os.path.join("static/images", filename))
        res = {"code": 0, "data": [filename]}
        return json.dumps(res)
    else:
        return ""


@app.route("/login", methods=["GET", "POST"])
def login():
    "登录方法"
    if request.method == "POST":
        username = request.form.get("username")
        if len(username) >= 0:
            pwd = request.form.get("pwd")
            conn = pymysql.connect(user=sqlHelper.get("user"), password=sqlHelper.get("pwd"),
                                   host=sqlHelper.get("host"), charset=sqlHelper.get("charset"))
            conn.select_db("blog")
            curr = conn.cursor()
            curr.execute("SELECT id FROM user_t WHERE username=%s AND password=%s", (username, pwd))
            conn.commit()
            results = curr.fetchall()
            flag = False
            if len(results) > 0:
                response = make_response(redirect("/index"))
                uid = results[0][0]
                if uid > 0:
                    response.set_cookie("uid", value=str(uid))
                    session["is_login"] = "1"
                    flag = True
                else:
                    session["is_login"] = "0"
            else:
                flag = False
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
        conn = pymysql.connect(user=sqlHelper.get("user"), password=sqlHelper.get("pwd"), host=sqlHelper.get("host"),
                               charset=sqlHelper.get("charset"))
        conn.select_db("blog")
        curr = conn.cursor()
        loginusername = session.get("loginusername")
        userimg = session.get("userimg")
        add_article = request.form.get("add_article")
        if add_article == "1":
            get_title = request.form.get("title")
            get_description = request.form.get("description")
            get_newtag = request.form.get("newtag")
            newtagIds = ""
            if len(get_newtag) > 0:
                newtagList = get_newtag.split(",")
                for t in newtagList:
                    curr.execute("SELECT COUNT(id),id FROM tag_t WHERE tag=%s", (t,))
                    conn.commit()
                    results = curr.fetchall()
                    nums = results[0][0]
                    if nums == 0:
                        curr.execute("INSERT INTO tag_t(tag) VALUES (%s)", (t,))
                        newtagIds += "," + str(conn.insert_id())
                        conn.commit()
                    else:
                        newtagIds += "," + str(results[0][1])
            get_tag = request.form.getlist("tag_ckb")
            tagString = ",".join(get_tag)
            tagString = tagString + newtagIds
            get_upload = request.form.get("upload")
            get_content = request.form.get("content")
            createdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            curr.execute("INSERT INTO article_t(title, content, imgpath, readings, tags, createdate, description) "
                         "VALUES (%s, %s, %s, 0, %s, %s, %s)",
                         (get_title, get_content, get_upload, tagString, createdate, get_description))
            conn.commit()
            response = make_response(redirect("/index"))
            return response
        else:
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


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    "管理员专用后台管理登录"
    if request.form.get("login") == "1":
        r = request.form.get("username")
        c = request.form.get("pwd")
        if len(r) > 0 and len(c) > 0:
            c = util.genearteMD5(c)
            conn = pymysql.connect(user=sqlHelper.get("user"), password=sqlHelper.get("pwd"),
                                   host=sqlHelper.get("host"), charset=sqlHelper.get("charset"))
            conn.select_db("blog")
            curr = conn.cursor()
            curr.execute("SELECT * FROM ruler")
            conn.commit()
            result = curr.fetchall()
            if result[0][1] == r and result[0][2] == c:
                session["admin_login"] = "ruler_p"
                return redirect("/resource_display")
    else:
        return render_template("adminLogin.html", errorInfo="请登录")


@app.route("/resource_display", methods=["GET", "POST"])
def resource_display():
    "资源后台展示"
    login_user = session.get("admin_login")
    if login_user is not None and len(login_user) > 0:
        conn = pymysql.connect(user=sqlHelper.get("user"), password=sqlHelper.get("pwd"),
                               host=sqlHelper.get("host"), charset=sqlHelper.get("charset"))
        conn.select_db("blog")
        curr = conn.cursor()

        # 获取总浏览量
        curr.execute("SELECT COUNT(id) FROM guest_t")
        conn.commit()
        result = curr.fetchall()
        visiter_sum = result[0][0]

        # 获取当日目前的浏览量
        today = datetime.datetime.now().strftime("%Y-%m-%d")+"%"
        curr.execute("SELECT COUNT(id) FROM guest_t WHERE visitTime LIKE %s", (today,))
        conn.commit()
        result = curr.fetchall()
        visiter_today = result[0][0]

        # 获取近30天每天的浏览量
        today = datetime.datetime.now().strftime("%Y-%m-%d")+"%"
        curr.execute("SELECT COUNT(id) FROM guest_t WHERE visitTime LIKE %s", (today,))
        conn.commit()
        result = curr.fetchall()
        visiter_today = result[0][0]

        return render_template("resourceDisplay.html")
    else:
        return render_template("adminLogin.html", errorInfo="请登录")


@app.route("/resource_display_table", methods=["GET", "POST"])
def resource_display_table():
    "资源后台列表展示"
    login_user = session.get("admin_login")
    if login_user is not None and len(login_user) > 0:
        return render_template("resourceDisplayTable.html")
    else:
        return render_template("adminLogin.html", errorInfo="请登录")


@app.route("/resource_display_local", methods=["GET", "POST"])
def resource_display_local():
    "显示服务器资源信息"
    login_user = session.get("admin_login")
    if login_user is not None and len(login_user) > 0:
        sys_os = platform.system()
        sysimg = ""
        if sys_os == "Windows":
            sysimg = url_for("static", filename="images/logo/windows.png")
        if sys_os == "Darwin":
            sysimg = url_for("static", filename="images/logo/apple.png")
        if sys_os == "Linux":
            sysimg = url_for("static", filename="images/logo/linux.png")
            sysNameStr = (platform.platform()).lower()
            if "centos" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/centOS.png")
            if "debian" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/debian.png")
            if "deepin" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/deepin.png")
            if "fedora" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/fedora.png")
            if "redhat" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/redhat.png")
            if "suse" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/suse.png")
            if "ubuntu" in sysNameStr:
                sysimg = url_for("static", filename="images/logo/ubuntu.png")
        pc_mem = psutil.virtual_memory()
        total_mem = "%.2f" % (pc_mem.total / (1024**3))
        used_mem = "%.2f" % (pc_mem.used / (1024**3))
        free_mem = "%.2f" % ((pc_mem.total-pc_mem.used) / (1024**3))
        pc_disk = psutil.disk_usage("/")
        total_disk = "%.2f" % (pc_disk.total / (1024**3))
        used_disk = "%.2f" % (pc_disk.used / (1024**3))
        free_disk = "%.2f" % (pc_disk.free / (1024**3))
        if sys_os == "Windows":
            prom = [0, 0, 0]
            pc = psutil.disk_partitions()
            for i in pc:
                pc_disk = psutil.disk_usage(i[0])
                prom[0] = prom[0] + pc_disk[0]
                prom[1] = prom[1] + pc_disk[1]
                prom[2] = prom[2] + pc_disk[2]
            total_disk = "%.2f" % (prom[0] / (1024 ** 3))
            used_disk = "%.2f" % (prom[1] / (1024 ** 3))
            free_disk = "%.2f" % (prom[2] / (1024 ** 3))
        return render_template("/resourceDisplayLocal.html", sysimg=sysimg, total_mem=total_mem, used_mem=used_mem,
                               free_mem=free_mem, total_disk=total_disk, used_disk=used_disk, free_disk=free_disk)
    else:
        return render_template("adminLogin.html", errorInfo="请登录")


@app.route("/test_data", methods=["GET", "POST"])
def test_data():
    "资源后台列表展示"
    uid = request.args.get("uid")
    if uid is not None and len(uid) > 0:
        list1 = [{"id": 10000, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10001, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10002, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10003, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10004, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10005, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10006, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10007, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10008, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10009, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10010, "aid": 1234, "time": "2018-03-19 17:41:35"},
                 {"id": 10011, "aid": 1234, "time": "2018-03-19 17:41:35"}]
        map1 = {"code": 0, "msg": "", "count": 12, "data": list1}
        return json.dumps(map1)
    else:
        list1 = [{"id": 10000, "ipadd": "1.203.80.98", "pro": "江西", "city": "南昌", "time": "2018-03-30"},
                 {"id": 10001, "ipadd": "1.203.80.98", "pro": "北京", "city": "北京", "time": "2018-03-30"},
                 {"id": 10002, "ipadd": "1.203.80.98", "pro": "北京", "city": "北京", "time": "2018-03-30"},
                 {"id": 10003, "ipadd": "1.203.80.98", "pro": "上海", "city": "上海", "time": "2018-03-30"},
                 {"id": 10004, "ipadd": "1.203.80.98", "pro": "江苏", "city": "南京", "time": "2018-03-30"},
                 {"id": 10005, "ipadd": "1.203.80.98", "pro": "浙江", "city": "杭州", "time": "2018-03-30"},
                 {"id": 10006, "ipadd": "1.203.80.98", "pro": "上海", "city": "上海", "time": "2018-03-30"},
                 {"id": 10007, "ipadd": "1.203.80.98", "pro": "北京", "city": "北京", "time": "2018-03-30"},
                 {"id": 10008, "ipadd": "1.203.80.98", "pro": "福建", "city": "厦门", "time": "2018-03-30"},
                 {"id": 10009, "ipadd": "1.203.80.98", "pro": "安徽", "city": "合肥", "time": "2018-03-30"},
                 {"id": 10010, "ipadd": "1.203.80.98", "pro": "江苏", "city": "苏州", "time": "2018-03-30"},
                 {"id": 10011, "ipadd": "1.203.80.98", "pro": "上海", "city": "上海", "time": "2018-03-30"}]
        map1 = {"code": 0, "msg": "", "count": 12, "data": list1}
        return json.dumps(map1)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
