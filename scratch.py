from flask import Flask, request, render_template, redirect, flash, session
import os
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)



@app.route('/')
def home():
    conn = sql.connect("db.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("Select * From urun")
    rows = cur.fetchall()
    return render_template('home.html', urunler = rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        con = sql.connect('db.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("Select * from user")
        Rows = cur.fetchall()
        for row in Rows:
            if request.form['email'] == row['email'] and check_password_hash(row['password'], request.form['password']):
                session['user'] = row['fullname']
                session['id'] = row['id']
                session['loggin'] = True
                session['shopping-cart'] = []
                session['role'] = row['role']
                break
        if not session.get('loggin'):
            flash("Kullanici Adiniz veya Sifreniz Hatalidir!")
            return redirect('/login')
        else:
            return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        email = request.form['email']
        fullname = request.form['fullname']
        password = generate_password_hash(request.form['password'])
        conn = sql.connect('db.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO USER (email, fullname, password) values (?,?,?)", (email, fullname, password))
        conn.commit()
        flash('KaydÄ±nÄ±z baÅŸarÄ±yla tamamlanmÄ±ÅŸtÄ±r')
        return redirect('/login')

@app.route('/logout', methods=['GET'])
def logout():
    session['user'] = ""
    session['loggin'] = False
    session['shopping-cart'] = []
    return redirect('/')

@app.route('/sepetekle/<int:id>')
def sepetekle(id):
    array = session.get('shopping-cart')
    array.append(id)
    session['shopping-cart'] = array
    return redirect('/')

@app.route('/adminpanel')
def adminpanel():
    conn = sql.connect("db.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("Select * From urun")
    rows = cur.fetchall()
    return render_template('adminpanel.html', urunler = rows)

@app.route('/kullanicipanel')
def kullanicipanel():
    return  render_template('kullanicipanel.html')

@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if request.method == "GET":
        return render_template('addproduct.html')
    elif request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        img = request.form['img']
        conn = sql.connect('db.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO urun (name, price, img) values (?,?,?)", (name, price, img))
        conn.commit()
        return redirect('/adminpanel')

@app.route('/editproduct/<int:id>', methods=['GET', 'POST'])
def editproduct(id):
    if request.method == "GET":
        con = sql.connect('db.db')
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM urun where id=?', (str(id)))
        rows = cur.fetchall()
        return render_template('editproduct.html', urun=rows[0])
    elif request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        img = request.form['img']
        conn = sql.connect('db.db')
        cur = conn.cursor()
        cur.execute('UPDATE urun set name=?, price=?, img=? where id=?', (name, price,img, id))
        conn.commit()
        return redirect('/adminpanel')

@app.route('/deleteproduct/<id>')
def deleteproduct(id):
    conn = sql.connect('db.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM urun where id=?", (id))
    conn.commit()
    return redirect('/adminpanel')

@app.route('/cart')
def cart():
    total = 0
    cart = session.get('shopping-cart')
    products = []
    con = sql.connect("db.db")
    cur = con.cursor()
    for id in cart:
        cur.execute("Select * from urun where id=?", (str(id)))
        rows = cur.fetchall()
        total += rows[0][2]
        products.append(rows[0])
    return render_template('cart.html', products = products, total = total)

@app.route('/clearcart')
def clearcart():
    session['shopping-cart'] = []
    return redirect('/cart')

@app.route('/odeme')
def odeme():
    session['shopping-cart'] = []
    return render_template('odeme.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)