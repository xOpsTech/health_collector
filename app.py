import json
import os
import constatnts
from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from HealthCalculator import HealthCalculator

if __name__ == '__main__':
    configs = os.getenv('configs')
    if configs is None:
        print('Exiting due to missing configs')
        exit()

    try:
        configs_json = json.loads(configs)
    except:
        configs_json = dict()

    tenant_id = configs_json.get('tenant', 'xtenant')

    SCHEDULER_INTERVAL = constatnts.SCHEDULER_INTERVAL  # in seconds
    executors = {
        'default': ThreadPoolExecutor()
    }

    healthCalculator = HealthCalculator(tenant_id)
    healthCalculator.start()

    app_scheduler = BlockingScheduler(executors=executors, timezone=utc)
    app_scheduler.add_job(healthCalculator.start, 'interval', seconds=SCHEDULER_INTERVAL,
                          id='health collector scheduler')
    app_scheduler.start()
