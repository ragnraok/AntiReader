from antireader.database import db
from antireader.feedutil import FeedData
#from antireader.app import task_app as app
from app import task_app as app

import datetime

def update_feed(site_id):
    from antireader.models import FeedSite, Article
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
            db.session.commit()
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
        app.logger.info("finish update site for id %d", site_id)

if __name__ == '__main__':
    from antireader.models import FeedSite
    sites = FeedSite.query.all()
    id_list = [s.id for s in sites]
    for i in id_list:
        try:
            update_feed(i)
        except:
            continue
