from flask import Flask, render_template, request, flash, redirect, abort, get_flashed_messages, url_for, Response
from dotenv import load_dotenv
from page_analyzer.db import Repository
from bs4 import BeautifulSoup
import psycopg, os, validators,  requests


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
        flash('Некорректный URL', 'danger')
        return render_template('index.html', name=name)
    if len(name) > 255 or not validators.url(name):
        flash('Неккоректный URL', 'danger')
        return render_template('index.html', name=name)
    if not repo.find_by_name(name):
        repo.save(name)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('index'))
    flash('Страница уже существует', 'info')
    return render_template('index.html')


@app.get('/urls')
def pages_index():
    urls = repo.all_posts()
    checks = repo.all_checks()

    last_checks = {}
    for check in checks:
        last_checks[check['url_id']] = check

    records = []
    for url in urls:
        check = last_checks.get(url['id'])
        records.append({
            'id': url['id'],
            'name': url['name'],
            'last_check': check['created_at'] if check else None,
            'status_code': check['status_code'] if check else None,
        })

    return render_template('websites.html', records=records)
    
    
@app.get('/urls/<id>')
def page_get(id):
    page = repo.find_by_id(id)
    checks = repo.all_checks_by_id(id)
    if page:
        return render_template('website.html', page=page, checks=checks)


@app.post('/urls/<id>/checks')
def page_get_post(id):
    page = repo.find_by_id(id)
    if page:
        url_id = page.get('id')
        try:
            try_access = requests.get(page['name'], timeout=5)
            try_access.raise_for_status()
            soup = BeautifulSoup(try_access.text, 'html.parser')
            heading_1 = soup.find('h1')
            if heading_1:
                heading_1_text = heading_1.text
            else:
                heading_1_text = "Не найден"
            title = soup.find('title')
            if title:
                title_text = heading_1.text[:200] + "..."
            else:
                title_text = "Не найден"
            description = soup.find('meta', attrs={'name': 'description'})
            if description:
                description_text = description['content'][:200] + "..."
            else:
                description_text = "Не найден"
            status_code = try_access.status_code
            repo.save_check(url_id, status_code, heading_1_text, title_text, description_text)
            flash('Страница успешно проверена', 'success')
        except requests.RequestException as re:
            flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('page_get', id=url_id))
    