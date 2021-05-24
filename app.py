from flask import Flask, render_template, session, url_for, request, redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'sample_secret'

def connectsql():
    conn = pymysql.connect(host='localhost', user = 'root', passwd = '1234', db = 'userlist', charset='utf8')
    return conn

@app.route('/')

def index():
    if 'username' in session:
        username = session['username']

        return render_template('index.html', logininfo = username)
    else:
        username = None
        return render_template('index.html', logininfo = username )

@app.route('/post')

def post():
    if 'username' in session:
        username = session['username']
    else:
        username = None
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT id, name, title, wdate, view FROM board ORDER BY id DESC" # ORDER BY 컬럼명 DESC : 역순출력, ASC : 순차출력
    cursor.execute(query)
    post_list = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('post.html', postlist = post_list, logininfo=username)

@app.route('/post/content/<id>')

def content(id):
    if 'username' in session:
        username = session['username']
        conn = connectsql()
        cursor = conn.cursor()
        query = "UPDATE board SET view = view + 1 WHERE id = %s"
        value = id
        cursor.execute(query, value)
        conn.commit()
        cursor.close()
        conn.close()

        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT id, title, content FROM board WHERE id = %s"
        value = id
        cursor.execute(query, value)
        content = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('content.html', data = content, username = username)
    else:
        return render_template ('Error.html')

@app.route('/post/edit/<id>', methods=['GET', 'POST'])

def edit(id):
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']

            edittitle = request.form['title']
            editcontent = request.form['content']

            conn = connectsql()
            cursor = conn.cursor()
            query = "UPDATE board SET title = %s, content = %s WHERE id = %s"
            value = (edittitle, editcontent, id)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()
    
            return render_template('editSuccess.html')
    else:
        if 'username' in session:
            username = session['username']
            conn = connectsql()
            cursor = conn.cursor()
            query = "SELECT name FROM board WHERE id = %s"
            value = id
            cursor.execute(query, value)
            data = [post[0] for post in cursor.fetchall()]
            cursor.close()
            conn.close()

            if username in data:
                conn = connectsql()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                query = "SELECT id, title, content FROM board WHERE id = %s"
                value = id
                cursor.execute(query, value)
                postdata = cursor.fetchall()
                cursor.close()
                conn.close()
                return render_template('edit.html', data=postdata, logininfo=username)
            else:
                return render_template('editError.html')
        else:
            return render_template ('Error.html')

@app.route('/post/delete/<id>')

def delete(id):
    if 'username' in session:
        username = session['username']
        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT name FROM board WHERE id = %s"
        value = id
        cursor.execute(query, value)
        data = [post[0] for post in cursor.fetchall()]
        cursor.close()
        conn.close()

        if username in data:
            return render_template('delete.html', id = id)
        else:
            return render_template('editError.html')
    else:
        return render_template ('Error.html')

@app.route('/post/delete/success/<id>')

def deletesuccess(id):
    conn = connectsql()
    cursor = conn.cursor()
    query = "DELETE FROM board WHERE id = %s"
    value = id
    cursor.execute(query, value)
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('post'))
    
@app.route('/write', methods=['GET', 'POST'])

def write():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            password = session['password']
            
            usertitle = request.form['title']
            usercontent = request.form['content']

            conn = connectsql()
            cursor = conn.cursor() 
            query = "INSERT INTO board (name, pass, title, content) values (%s, %s, %s, %s)"
            value = (username, password, usertitle, usercontent)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('post'))
        else:
            return render_template('errorpage.html')
    else:
        if 'username' in session:
            username = session['username']
            return render_template ('write.html', logininfo = username)
        else:
            return render_template ('Error.html')

@app.route('/logout')

def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])

def login():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        logininfo = request.form['id']
        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM tbl_user WHERE user_name = %s AND user_password = %s"
        value = (userid, userpw)
        cursor.execute(query, value)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for row in data:
            data = row[0]
        
        if data:
            session['username'] = request.form['id']
            session['password'] = request.form['pw']
            return render_template('index.html', logininfo = logininfo)
        else:
            return render_template('loginError.html')
    else:
        return render_template ('login.html')

@app.route('/regist', methods=['GET', 'POST'])

def regist():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM tbl_user WHERE user_name = %s"
        value = userid
        cursor.execute(query, value)
        data = (cursor.fetchall())
        
        if data:
            conn.rollback() 
            return render_template('registError.html') 
        else:
            query = "INSERT INTO tbl_user (user_name, user_password) values (%s, %s)"
            value = (userid, userpw)
            cursor.execute(query, value)
            data = cursor.fetchall()
            conn.commit()
            return render_template('registSuccess.html')
        cursor.close()
        conn.close()
    else:
        return render_template('regist.html')        

if __name__ == '__main__':
    app.run(host='0.0.0.0')