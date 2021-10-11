from apscheduler.schedulers.background import BackgroundScheduler

# XXX: Consider using prod database instead of a disposable sqlite
scheduler = BackgroundScheduler(
    {
        "apscheduler.jobstores.default": {
            "type": "sqlalchemy",
            "url": "sqlite:///jobs.sqlite",
        },
        "apscheduler.executors.default": {
            "class": "apscheduler.executors.pool:ThreadPoolExecutor",
            "max_workers": "20",
        },
        "apscheduler.executors.processpool": {
            "type": "processpool",
            "max_workers": "5",
        },
        "apscheduler.job_defaults.coalesce": "false",
        "apscheduler.job_defaults.max_instances": "3",
        "apscheduler.timezone": "Europe/Madrid",
    }
)
