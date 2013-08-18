from apscheduler.scheduler import Scheduler
from worker import add_update_task
from antireader.models import FeedSite

sched = Scheduler()

#@sched.cron_schedule(hour='0')
@sched.interval_schedule(hours=1)
def clock_task():
    # update all sites
    sites = FeedSite.query.all()
    id_list = [s.id for s in sites]
    for i in id_list:
        add_update_task(i)

if __name__ == '__main__':
    sched.start()
    while True:
        pass
