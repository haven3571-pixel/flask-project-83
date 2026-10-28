from flask import Flask, render_template, request, flash, redirect, abort, get_flashed_messages, url_for
from dotenv import load_dotenv
from page_analyzer.db import Repository
import psycopg, os, validators


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
repo = Repository()


@app.get('/')
def index():
    # error_messages = get_flashed_messages(category_filter=['error'])
    # success_messages = get_flashed_messages(category_filter=['success'])
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.post('/urls')
def pages_post():
    name = request.form.get('url')
    if name is None:
        flash('Неккоректный URL', 'error')
        return render_template('index.html', name=name)
    if len(name) > 255 or not validators.url(name):
        flash('Неккоректный URL', 'error')
        return render_template('index.html', name=name)
    if not repo.find_by_name(name):
        repo.save(name)
        flash('Адрес успешно добавлен', 'success')
        return redirect(url_for('index'))
    flash('URL-адрес уже был добавлен', 'error')
    return render_template('index.html')


@app.get('/urls')
def pages_index():
    records = repo.all_posts()
    if records:
        return render_template('websites.html', records=records)
    
    
@app.get('/urls/<id>')
def page_get(id):
    page = repo.find_by_id(id)
    if page:
        return render_template('website.html', page=page)