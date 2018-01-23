from flask import Flask, render_template, url_for, request, redirect, make_response, session
import os
import MySQLdb
import User


app = Flask(__name__)
app.secret_key = "abcde"

image_path = os.path.join(os.getcwd(), "static/images")


@app.route('/')
def index():
    islogin = session.get("is_login")
    cookies_uid = request.cookies.get("uid")
    conn = MySQLdb.connect(user="root", password="root", host="localhost", charset="utf8")
    conn.select_db("blog")
    curr = conn.cursor()
    curr.execute("SELECT id,navname FROM nav_t")
    conn.commit()
    results = curr.fetchall()
    nav_list = []
    for row in results:
        nav_list.append(row[1])
    curr.execute("SELECT id,title,content,imgpath,readings,createdate,tags,description FROM article_t ORDER BY id DESC")
    conn.commit()
    results = curr.fetchall()
    blog_list = []
    for row in results:
        blog = {}
        blog["id"] = row[0]
        blog["title"] = row[1]
        blog["content"] = row[2]
        if row[3] is not None:
            imgurl = "images/%s" % row[3]
            blog["imgpath"] = url_for("static", filename=imgurl)
        else:
            blog["imgpath"] = ""
        blog["readings"] = row[4]
        blog["createdate"] = row[5]
        blog["tags"] = row[6]
        blog["description"] = row[7]
        blog_list.append(blog)
    blog_size = len(blog_list)
    curr.execute("SELECT id,tag FROM tag_t")
    conn.commit()
    results = curr.fetchall()
    tag_list = []
    for row in results:
        tag_list.append(row[1])
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
    return render_template("index.html", nav_list=nav_list, loginusername=loginusername, userimg=userimg, userinfo=userinfo, blog=blog_list, blogtag=tag_list, blogsize=blog_size, islogin=islogin)


@app.route("/content")
def content():
    article_id = request.args.get("ai")
    conn = MySQLdb.connect(user="root", password="root", host="localhost", charset="utf8")
    conn.select_db("blog")
    curr = conn.cursor()
    curr.execute("")
    return render_template()


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        username = request.form["username"]
        file = request.files["img"]
        filename = file.filename
        file.save(os.path.join(image_path, filename))
        return "<img src='static/images/%s' alt=''/>" % username
    else:
        return render_template("upload.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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
            response = make_response(redirect("/"))
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
    session["is_login"] = "0"
    response = make_response(redirect("/"))
    response.delete_cookie("uid")
    return response


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8086)
