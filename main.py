from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string, sqlite3
from urlparse import urlparse

host = 'http://localhost:5000/'


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INT PRIMARY KEY     AUTOINCREMENT,
        URL  TEXT    NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass

def toBase62(num, b = 62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + string.lowercase + string.uppercase
    r = num % b
    res = base[r];
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res

def toBase10(num, b = 62):
    base = string.digits + string.lowercase + string.uppercase
    limit = len(num)
    res = 0
    for i in xrange(limit):
        res = b * res + base.find(num[i])
    return res

#Assuming urls.db is in your app root folder
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form.get('url')
        print urlparse(original_url)
        if urlparse(original_url).scheme == '':
            original_url = 'http://' + original_url
        print original_url 
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            insert_row = """
                INSERT INTO WEB_URL (URL)
                    VALUES ('%s')
                """%(original_url)
            result_cursor = cursor.execute(insert_row)
            encoded_string = toBase62(result_cursor.lastrowid)
        return render_template('home.html',short_url= host + encoded_string)
    return render_template('home.html')



@app.route('/<short_url>')
def redirect_short_url(short_url):
    import ipdb;ipdb.set_trace()
    decoded_string = toBase10(short_url)
    redirect_url = 'http://localhost:5000'
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
                SELECT URL FROM WEB_URL
                    WHERE ID=%s
                """%(decoded_string)
        result_cursor = cursor.execute(select_row)
        try:
            redirect_url = result_cursor.fetchone()[0]
        except Exception as e:
            print e
    return redirect(redirect_url)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    app.run(debug=True)