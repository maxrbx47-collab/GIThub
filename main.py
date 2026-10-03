import flask

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename


from flask import render_template

import sqlite3

import uuid
import requests
tool_icons = {
    "python": '🐍', 'flask': '🌶️', 'HTML': '📃', 'CSS': '🎨','HTML/CSS': '🖌️', 'Git': '🔧', 'GitHub': "🐙", 'Telegram': '✈️', 'SQL': "🗄️", 'SQLite': "📘", "JavaScript": "⚡", "JS": "⚡", "jinja": "🧩"

}


app = flask.Flask(__name__)
@app.route('/')
def index():
    connection = sqlite3.connect('danniye.db')
    cursor = connection.cursor()


    cursor.execute("SELECT uuid,name,avatar,bio,skills FROM portfolios")
    raw_data = cursor.fetchall()


    connection.close()

    filter_skill = request.args.get('skill')
    if filter_skill:
        filter_skill = filter_skill.strip().lower()
    else:
        filter_skill = None

    portfolios = []
    for uuid, name, avatar, bio, skills_str in raw_data:
        skills = []
        for s in skills_str.split(','):
            s = s.strip()
            if s:
                skills.append(s)

        skills_lower = []
        for s in skills:
            skills_lower.append(s.lower())

        if filter_skill is None or filter_skill in skills_lower:
            portfolios.append((uuid, name, avatar, bio, skills))

    return render_template("all_portfolios.html", portfolios=portfolios, tool_icons=tool_icons, current_skill=filter_skill or '')




@app.route('/form')
def form():
    return render_template('form.html')
@app.route("/generate", methods=["POST"])
def generate():
    form = request.form
    avatar = request.files.get("avatar")

    uid = str(uuid.uuid4())


    name = form["name"]
    bio = form["bio"]
    github = form["github"].strip().replace("https://github.com/", "").replace("/", "")
    telegram = form["telegram"]
    skills = form["skills"]

    avatar_filename = ""

    if avatar and avatar.filename:
        filename = secure_filename(f"{uid}_{avatar.filename}")
        avatar_path = f"static/uploads/{filename}"
        avatar.save(avatar_path)


        avatar_filename = avatar_path.replace("static/", "")


    conn = sqlite3.connect('danniye.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO portfolios (
            uuid,
            name,
            bio,
            github,
            telegram,
            avatar,
            skills
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        name,
        bio,
        github,
        telegram,
        avatar_filename,
        skills
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))
@app.route('/portfolio/<uuid>')
def view_portfolio(uuid,):
    conn = sqlite3.connect('danniye.db')
    c = conn.cursor()
    c.execute('SELECT name, bio, github, telegram, avatar, skills FROM portfolios WHERE uuid = ?', (uuid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "portfolio not found", 404

    name, bio, github, telegram, avatar, skills_str = row
    skills = []
    for s in skills_str.split(','):
        skills.append(s.strip())
    

    projects = []


    try:
        r = requests.get(f"https://api.github.com/users/{github}/repos")
        if r.ok:
            for repo in r.json()[:6]:
                projects.append({
                    'title': repo['name'],
                    'description': repo.get('description') or 'untitled',
                    'link': repo['html_url'],
                })
    except Exception as e:
        print('Github API error', e)

    return render_template("portfolio_template.html", name=name, bio=bio, github=github, telegram=telegram,
                           avatar=avatar, skills=skills, projects=projects, tool_icons=tool_icons)

if __name__ == '__main__':
    app.run()

