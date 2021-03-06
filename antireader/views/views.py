# -*- coding: utf-8 -*-
from flask import Blueprint, g, current_app, redirect, url_for, flash, \
    request, render_template, jsonify
from flask.ext import login as _login
from form import LoginForm
from antireader.models import FeedSite, Article, StarArticle
from utils import generate_article_link, unauthorize_response, response_html, ajax_response
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
        user = form.get_user(current_app)
        if user is None:
            flash("Invalid user")
            return render_template("login.html", form=form)
        if not user.verify(form.username.data, form.password.data):
            flash("Invalid password")
            return render_template('login.html', form=form)
        # success login user
        _login.login_user(user, remember=True)
        return redirect(url_for(".timeline"))
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
        'id': item.id, 'site': item.site.title} for item in articles]
    article_info = {'length': Article.query.count(), 'show_button_min_length': default_article_num}
    return render_template("timeline.html", article_list=article_list,
            article_info=article_info, sourcelist_link=url_for(".sourcelist"),
            star_articles_link=url_for('.fav_articles_list'))

@app.route("/load_article/<int:article_id>/")
def article_view(article_id):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    article = Article.query.get(article_id)
    if article:
        article_info = {'title': article.title, 'source': article.site.title, 'content': article.content,
                'link': article.link, 'updated': article.updated.strftime("%Y-%m-%d"),
                'site_link': "#", 'id': article.id,
                'star_prompt': article.is_star() and '取消收藏'.decode('utf8') or '收藏'.decode('utf8')}
        return render_template("article_view.html", article=article_info)
    else:
        return None

@app.route("/load_fav_article/<int:article_id>/")
def fav_article_view(article_id):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    article = StarArticle.query.get(article_id)
    if article:
        article_info = {'title': article.title, 'content': article.content,
                'link': article.link,
                'updated': article.updated.strftime("%Y-%m-%d"),
                'id': article.id,
                'star_prompt': '取消收藏'.decode('utf8')}
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
        print len(articles)
        articles_info = []
        for item in articles:
            _dict = {'name': item.title, 'id': item.id, 'site': item.site.title}
            articles_info.append(_dict)
        if len(articles_info) < current_app.config['PER_PAGE_ARTICLE_NUM']:
            last_page = True
        else:
            last_page = False;
        return ajax_response(success=True, data={'last_page': last_page, 'info': articles_info})
    else:
        return ajax_response(success=True, data={'last_page': last_page, 'info': []})

@app.route("/sourcelist/")
@_login.login_required
def sourcelist():
    sites = FeedSite.query.all()
    info = []
    for s in sites:
        _dict = {'title': s.title,
                'updated': s.updated.strftime("%Y-%m-%d"),
                'link': "/siteview/%d/%d" % (s.id, 0)}
        articles = s.articles
        article_info = []
        for a in articles[:3]:
            article_dict = {'link': generate_article_link(s.id, a.id),
                    'title': a.title, 'id': a.id}
            article_info.append(article_dict)
        _dict['articles'] = article_info
        _dict['id'] = s.id
        info.append(_dict)
    return render_template("sourcelist.html", source_list=info, sourcelist_link="#",
            star_articles_link=url_for('.fav_articles_list'))

@app.route("/sourcelist/unsubscribe/<int:site_id>/", methods=("POST", ))
def unsubscribe(site_id):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    if FeedSite.delete_site(site_id):
        return ajax_response(success=True)
    return ajax_response(success=False)

@app.route("/subscribe/", methods=("POST", ))
def subscribe():
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    url = request.form['site']
    #print request.get_json(force=True)
    print url
    try:
        FeedSite.create_site(url)
        return ajax_response(success=True)
    except:
        return ajax_response(success=False)

@app.route("/siteview/<int:site_id>/")
@_login.login_required
def siteview(site_id):
    site = FeedSite.query.get(site_id)
    if site:
        articles = site.articles.order_by(desc(Article.updated)).all();
        # construct article_list
        article_list = []
        for item in articles:
            _dict = {'id': item.id, 'name': item.title, 'site': site.title}
            article_list.append(_dict)
        return render_template('siteview.html', article_list=article_list,
                sourcelist_link=url_for(".sourcelist"),
                star_articles_link=url_for('.fav_articles_list'))

        #if article_id == 0:
        #    selected_article_id = articles[0].id
        #else:
        #    selected_article_id = article_id

        #article = Article.query.get(selected_article_id)
        #if article:
        #    article_info = {'title': article.title, 'site_link': site.url,
        #           'source': site.title, 'updated': article.updated.strftime("%Y-%m-%d"),
        #           'content': article.content, 'link': article.link}
        #return render_template('siteview.html',
        #        selected_id=selected_article_id,
        #        article_list=article_list, article=article_info,
        #        sourcelist_link=url_for(".sourcelist"))


#@app.route("/start_article/<int:article_id>/", methods=("POST", ))
#def start_article(article_id):
#    pass
#
#@app.route("/unstart_article/<int:start_article_id>/", methods=("POST", ))
#def unstart_article(start_article_id):
#    pass

@app.route("/toggle_star_article/<int:article_id>/<int:mode>", methods=('POST', ))
def toggle_star_article(article_id, mode):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    if mode == 0:
        article = Article.query.get(article_id)
        if article:
            if article.is_star():
                start_article = StarArticle.get_from_article(article.title)
                start_article.unstar()
                return ajax_response(success=True, data={'star': False})
            else:
                article.star()
                return ajax_response(success=True, data={'star': True})
    elif mode == 1:
        star_article = StarArticle.query.get(article_id)
        if star_article:
            star_article.unstar()
            return ajax_response(success=True, data={'star': False})

    return ajax_response(success=False)


@app.route("/fav_article_list/")
@_login.login_required
def fav_articles_list():
    default_article_num = current_app.config['DEFAULT_ARTICLE_SHOW_NUM']
    if StarArticle.query.count() >= default_article_num:
        articles = StarArticle.query.order_by(desc(StarArticle.updated)).slice(0, default_article_num - 1).all()
    else:
        articles = StarArticle.query.order_by(desc(StarArticle.updated)).all()
    article_list = [{'name': item.title,
        'content': item.content, 'link': "#",
        'id': item.id, 'site': item.site} for item in articles]
    article_info = {'length': StarArticle.query.count(), 'show_button_min_length': default_article_num}
    return render_template("fav_articles_list.html", article_list=article_list,
            article_info=article_info, sourcelist_link=url_for(".sourcelist"),
            star_articles_link="#")

@app.route("/fav_article_list/load_articles/<int:page>/")
def load_fav_articles(page):
    if not _login.current_user.is_authenticated():
        # redirect to login
        return unauthorize_response
    if page >= 1:
        articles = StarArticle.query.order_by(desc(StarArticle.updated)).offset(
                current_app.config['DEFAULT_ARTICLE_SHOW_NUM'] - 1).from_self(
                       ).paginate(page=page, per_page=current_app.config['PER_PAGE_ARTICLE_NUM']).items
        print len(articles)
        articles_info = []
        for item in articles:
            _dict = {'name': item.title, 'id': item.id, 'site': item.site}
            articles_info.append(_dict)
        if len(articles_info) < current_app.config['PER_PAGE_ARTICLE_NUM']:
            last_page = True
        else:
            last_page = False;
        return ajax_response(success=True, data={'last_page': last_page, 'info': articles_info})
    else:
        return ajax_response(success=True, data={'last_page': last_page, 'info': []})
