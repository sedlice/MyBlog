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
        username = ""
        userimg = url_for("static", filename="images/unknownuser.png")
    else:
        username = cookies_username
        userimg = url_for("static", filename="images/168.jpg")
    userinfo = {"username": username, "userimg": userimg}
    islogin = session.get("is_login")
    nav_list = [u"首页", u"经济", u"文化", u"科技", u"娱乐"]
    blog_list = [{"title": "欢迎来到我的博客", "content": "博客的第二篇文章（测试）", "createDate": "1月17日", "reads": "15", "img": url_for("static", filename="images/cat.jpg")},
            {"title": "第二篇文章", "content": "这是我博客的第一篇文章（测试）", "createDate": "1月9日", "reads": "5", "img": ""}]
    blog_size = len(blog_list)
    blog_tag = {"javascript": "10", "python": "50", "shell": "5"}
    return render_template("index.html", nav_list=nav_list, userinfo=userinfo, blog=blog_list, blogtag=blog_tag, blogsize=blog_size, islogin=islogin)


@app.route("/content")
def content():
    article_id = request.args.get("ai")
    conn = MySQLdb.connect(user="root", password="root", host="localhost")
    conn.select_db("test")
    curr = conn.cursor()
    curr.execute("")
    return render_template()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        age = request.form.get("age")
        conn = MySQLdb.connect(user="root", password="root", host="localhost")
        conn.select_db("test")
        curr = conn.cursor()
        curr.execute("INSERT INTO user_t(user_name, password, age) VALUES ('%s', '%s', %d)", username, pwd, int(age))
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
        if len(username) >= 0:
            pwd = request.form["pwd"]
            print("username=%s,pwd=%s" % (username, pwd))
            conn = MySQLdb.connect(user="root", password="root", host="localhost")
            conn.select_db("test")
            curr = conn.cursor()
            curr.execute("SELECT user_name FROM user_t WHERE user_name='%s' AND password='%s'", username, pwd)
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
                return render_template("login.html", username=username, tips="用户名或密码错误")
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session["is_login"] = "0"
    response = make_response(redirect("/"))
    response.delete_cookie("username")
    return response


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
