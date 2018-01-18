from flask import Flask, render_template, url_for, request, redirect, make_response, session
import os
import MySQLdb


app = Flask(__name__)
app.secret_key = "abcde"

image_path = os.path.join(os.getcwd(), "static/images")


@app.route('/')
def index():
    cookies_username = request.cookies.get("username")
    if not cookies_username:
        # return redirect("/login")
        username = "请登录"
    else:
        username = cookies_username
    islogin = session.get("is_login")
    nav_list = [u"首页", u"经济", u"文化", u"科技", u"娱乐"]
    blog = {"title": "欢迎来到我的博客", "content": "Hello"}
    blogtag = {"javascript": "10", "python": "50", "shell": "5"}
    img = url_for("static", filename="images/cat.jpg")
    return render_template("index.html", nav_list=nav_list, username=username, blog=blog, blogtag=blogtag, img=img, islogin=islogin)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        pwd = request.form["pwd"]
        age = request.form["age"]
        conn = MySQLdb.connect(user="root", password="root", host="localhost")
        conn.select_db("test")
        curr = conn.cursor()
        sql = "INSERT INTO user_t(user_name, password, age) VALUES ('%s', '%s', %d)" % (username, pwd, int(age))
        curr.execute(sql)
        conn.commit()
        curr.close()
        conn.close()
        return redirect("/login")
    else:
        return render_template("register.html")


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
        pwd = request.form["pwd"]
        print("username=%s,pwd=%s" % (username, pwd))
        conn = MySQLdb.connect(user="root", password="root", host="localhost")
        conn.select_db("test")
        curr = conn.cursor()
        sql = "SELECT user_name FROM user_t WHERE user_name='%s' AND password='%s'" % (username, pwd)
        curr.execute(sql)
        conn.commit()
        results = curr.fetchall()
        flag = False
        response = make_response(redirect("/"))
        for row in results:
            if username == row[0]:
                response.set_cookie("username", value=username, max_age=300)
                session["is_login"] = "1"
                flag = True
                break
            else:
                session["is_login"] = "0"
        curr.close()
        conn.close()
        if flag:
            return response
        else:
            return redirect("/login")
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear
    response = make_response(redirect("/"))
    response.delete_cookie("username")
    return response


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
