"""API for audio projects."""
import flask
import wave
import sqlite3
import os
import datetime
from io import BytesIO
import math
from zipfile import ZipFile

app = flask.Flask(__name__)
#count = 0


def get_db_connection():
    # connect to database
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    context = {"text": "Hello!"}
    return flask.render_template("index.html", **context)


@app.route('/post', methods=['POST'])
def post():
    # read .wav file
    file = flask.request.files['file']

    with wave.open(file, 'rb') as handle:
        params = handle.getparams()
        duration = (1/handle.getframerate()) * handle.getnframes()
        frames = handle.readframes(handle.getnframes())
    with wave.open(f"uploads/{file.filename}", "wb") as handle:
        handle.setparams(params)
        handle.writeframes(frames)

    # update database
    if not os.path.isfile('database.db'):
        connection = sqlite3.connect('database.db')
        with open('schema.sql') as f:
            connection.executescript(f.read())
    else:
        connection = sqlite3.connect('database.db')

    cur = connection.cursor()
    cur.execute("INSERT INTO audio (filename, duration) VALUES (?, ?)",
                (file.filename, duration))
    connection.commit()
    connection.close()

    '''
    Read raw audio bytes and convert/save to a .wav file:

    global count
    raw_data = flask.request.get_data()   
    with wave.open(f"uploads/sound{count}.wav", "wb") as out_f:
            out_f.setnchannels(1)
            out_f.setsampwidth(2) # number of bytes
            out_f.setframerate(44100)
            out_f.writeframesraw(raw_data)
            count += 1    
    '''
    # return '', 201
    return flask.redirect("/list")


@app.route('/download')
def download():
    # get arguments (if provided)
    name_filter = flask.request.args.get('name', default="", type=str)
    duration_filter = flask.request.args.get(
        'maxduration', default=-1, type=int)

    # connect to database
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM audio').fetchall()

    filenames = []

    # query appropriate rows
    for row in posts:
        postid = row[0]
        created = row[1]
        duration = row[2]
        filename = row[3]

        if name_filter != "":
            if duration_filter != -1:
                if filename == name_filter and duration <= duration_filter:
                    filenames.append(filename)
            elif filename == name_filter:
                filenames.append(filename)
        else:
            if duration_filter != -1:
                if duration <= duration_filter:
                    filenames.append(filename)
            else:
                filenames.append(filename)

    conn.close()

    # create zip file
    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zipObj:
        for filename in filenames:
            zipObj.write(f"uploads/{filename}")

    memory_file.seek(0)
    return flask.send_file(memory_file, download_name="stored_files.zip", as_attachment=True, mimetype="application/zip")


@app.route('/list')
def list():
    # get arguments (if provided)
    name_filter = flask.request.args.get('name', default="", type=str)
    duration_filter = flask.request.args.get(
        'maxduration', default=-1, type=int)

    # connect to database
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM audio').fetchall()

    context = {}

    # query appropriate rows
    for row in posts:
        postid = row[0]
        created = row[1]
        duration = row[2]
        filename = row[3]

        if name_filter != "":
            if duration_filter != -1:
                if filename == name_filter and duration <= duration_filter:
                    context[postid] = filename
            elif filename == name_filter:
                context[postid] = filename
        else:
            if duration_filter != -1:
                if duration <= duration_filter:
                    context[postid] = filename
            else:
                context[postid] = filename

    conn.close()

    return flask.jsonify(context), 200


@app.route('/info')
def info():
    # get arguments (if provided)
    name_filter = flask.request.args.get('name', default="", type=str)
    duration_filter = flask.request.args.get(
        'maxduration', default=-1, type=int)

    # connect to database
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM audio').fetchall()

    context = {}

    # query appropriate rows
    for row in posts:
        postid = row[0]
        created = row[1]
        duration = math.floor(int(row[2]))
        filename = row[3]

        time = str(datetime.timedelta(seconds=duration))
        context2 = {"timestamp": created, "duration": time}

        if name_filter != "":
            if duration_filter != -1:
                if filename == name_filter and duration <= duration_filter:
                    context[filename] = context2
            elif filename == name_filter:
                context[filename] = context2
        else:
            if duration_filter != -1:
                if duration <= duration_filter:
                    context[filename] = context2
            else:
                context[filename] = context2

    conn.close()

    return flask.jsonify(context), 200
