from apscheduler.scheduler import Scheduler

sched = Scheduler(daemonic=False)

#@sched.cron_schedule(hour='0')
@sched.interval_schedule(hours=1)
def clock_task():
    from worker import add_update_task
    from antireader.models import FeedSite
    # update all sites
    sites = FeedSite.query.all()
    id_list = [s.id for s in sites]
    for i in id_list:
        add_update_task(i)

def start_clock():
    sched.start()
