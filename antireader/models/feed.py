# -*- coding: utf-8 -*-
from antireader.database import db
from antireader.feedutil import FeedData, get_feed_link, CannotGetFeedSite
from antireader.task import add_update_task
from flask import current_app as app

import datetime

class FeedSite(db.Model):
    __tablename__ = 'feedsite'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False, unique=True)
    updated = db.Column(db.DateTime, default=datetime.datetime.now)
    articles = db.relationship('Article', backref=db.backref('feedsite',
        lazy="joined"), lazy='dynamic', cascade="all,delete")

    def __init__(self, url):
        feed_link = get_feed_link(url)
        if feed_link is None:
            raise CannotGetFeedSite(url)
        self.url = feed_link
        feed_data = FeedData(feed_link, True)
        feed_data.init_data()
        self.title =  feed_data.site_title
        updated = feed_data.site_updated
        if updated is not None:
            self.updated = updated
        else:
            self.updated = datetime.datetime.now()

    @classmethod
    def create_site(cls, url):
        # first check if exist the same site
        feed_link = get_feed_link(url)
        if feed_link is None:
            raise CannotGetFeedSite(url)
        if FeedSite.query.filter_by(url=feed_link).count() > 0:
            return

        site = FeedSite(url)
        db.session.add(site)
        db.session.commit()
        add_update_task(site.id)

    def __repr__(self):
        return "<Site: %s>" % (self.title, )

    def __str__(self):
        return "<Site: %s>" % (self.title, )

    @classmethod
    def add_site(cls, url):
        new_site = FeedSite(url)
        db.session.add(new_site)
        db.session.delete(new_site)

    @classmethod
    def delete_site(cls, site):
        db.session.delete(site)
        db.session.commit()

    @classmethod
    def add_site_list(cls, sites):
        if sites:
            for s in sites:
                db.session.add(s)
            db.session.commit()

    @classmethod
    def delete_site_list(cls, sites):
        if sites:
            for s in sites:
                db.session.delete(s)
            db.session.commit()

class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('feedsite.id', ondelete='CASCADE'))
    link = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    content = db.Column(db.Text, nullable=False)
    site = db.relationship('FeedSite', innerjoin=True, lazy="joined")

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<Article: %s>" % (self.title, )

    def __str__(self):
        return "<Article: %s>" % (self.title, )

    @classmethod
    def delete_articles(cls, articles):
        if articles:
            for a in articles:
                db.session.delete(a)
            db.session.commit()

    @classmethod
    def add_articles(cls, articles):
        if articles:
            for a in articles:
                db.session.add(articles)
            db.session.commit()
