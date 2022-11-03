# Deepgram-Coding-Project
Deepgram Summer 2023 Internship Coding Project

Project completed using Python, Flask, SQLite3, and the Python Wave Module (among others).

Endpoints: post, download, list, info

To make a post request: 
curl -X POST -F file=@filename.wav http://localhost:8000/post

To run server:
```
export FLASK_ENV=development
export FLASK_APP=index 
flask run --host 0.0.0.0 --port 8000
```
