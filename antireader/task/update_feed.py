from antireader.models import FeedSite, Article
from anitreader.feedutil import FeedData
from antireader.app import db

import datatime

def update_feed(site_id, app):
    if app:
        with app.app_context():
            site = FeedSite.query.get(site_id)
            if site is None:
                app.logger.error("site for id %d is not exist!" % (site_id, ))
                return
            site_url = site.url
            feed_data = FeedData(site_url, True)
            feed_data.init_data()
            old_updated = site.updated
            new_updated = feed_data.site_updated
            if new_updated is None or new_updated > old_updated or site.articles.count() == 0:
                if new_updated is None:
                    site.updated = datetime.datetime.now()
                else:
                    site.updated = new_updated
                db.session.add(site)
                db.session.commit(site)
            new_articles = feed_data.site_articles
            articles = site.articles.all()
            # delete old articles
            Article.delete_articles(articles)
            # add new articles
            for item in new_articles:
                article = Article(site_id=site_id, link=item['link'],
                        title=item['title'], updated=item['date'],
                        content=item['content'])
                db.session.add(article)
            db.session.commit()
