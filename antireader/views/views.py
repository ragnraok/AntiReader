from flask import Blueprint, g, current_app, redirect, url_for, flash, \
    request, render_template, jsonify
from flask.ext import login as _login
from form import LoginForm
from antireader.models import FeedSite, Article
from utils import generate_article_link, unauthorize_response, response_html
from sqlalchemy.sql.expression import desc

app = Blueprint("web", __name__)

@app.route("/", methods=("GET", ))
def index():
    if not _login.current_user.is_authenticated():
        # redirect to login
        return redirect(url_for(".login"))
    else:
        # redirect to timeline
        return redirect(url_for(".timeline"))

@app.route("/login/", methods=("GET", "POST"))
def login():
    form = LoginForm(request.form)
    print form.username.data
    if form.validate_on_submit():
        print "success submit form"
        user = form.get_user(current_app)
        print "user = %s" % str(user)
        if user is None:
            flash("Invalid user")
            return render_template("login.html", form=form)
        if not user.verify(form.username.data, form.password.data):
            flash("Invalid password")
            return render_template('login.html', form=form)
        # success login user
        _login.login_user(user, remember=True)
        return redirect(url_for(".timeline"))
    print "fail to submit form"
    return render_template("login.html", form=form)

@app.route("/logout/", methods=("GET", ))
@_login.login_required
def logout():
    _login.logout_user()
    return redirect(url_for(".login"))

@app.route("/timeline/", methods=("GET", "POST"))
@_login.login_required
def timeline():
    # here just return the first 30 articles
    default_article_num = current_app.config['DEFAULT_ARTICLE_SHOW_NUM']
    if Article.query.count() >= default_article_num:
        articles = Article.query.order_by(desc(Article.updated)).slice(0, default_article_num - 1).all()
    else:
        articles = Article.query.order_by(desc(Article.updated)).all()
    article_list = [{'name': item.title,
        'content': item.content, 'link': "#",
        'id': item.id} for item in articles]
    article_info = {'length': Article.query.count(), 'show_button_min_length': default_article_num}
    return render_template("timeline.html", article_list=article_list,
            article_info=article_info)

@app.route("/timeline/<article_id>")
def article_view(article_id):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    article = Article.query.get(article_id)
    if article:
        article_info = {'title': article.title, 'source': article.site.title, 'content': article.content,
                'link': article.link, 'updated': article.updated.strftime("%Y-%m-%d"),
                'site_link': article.site.url}
        return render_template("article_view.html", article=article_info)
    else:
        return None

@app.route("/timeline/load_articles/<int:page>/")
def load_article(page):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    if page >= 1:
        articles = Article.query.order_by(desc(Article.updated)).offset(
                current_app.config['DEFAULT_ARTICLE_SHOW_NUM'] - 1).from_self(
                       ).paginate(page=page, per_page=current_app.config['PER_PAGE_ARTICLE_NUM']).items
        articles_info = []
        for item in articles:
            _dict = {'name': item.title, 'id': item.id}
            articles_info.append(_dict)
        if len(articles_info) < current_app.config['PER_PAGE_ARTICLE_NUM']:
            last_page = True
        else:
            last_page = False;
        return jsonify(info=articles_info, last_page=last_page)
    else:
        return jsonify(info=[])

@app.route("/sourcelist/")
def sourcelist():
    pass
