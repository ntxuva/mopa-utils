# CRON configuration

## View cron log

```sh
grep CRON /var/log/syslog | tail
```

## Edit schedule with

```sh
crontab -e
```

## Schedule to be set

```sh
# min hour day-of-month month day-of-week command
*/5 * * * * /srv/www/mopa-utils/jobs/notify_updates_on_requests.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
# 30 15 * * * /srv/www/mopa-utils/jobs/send_daily_survey.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
# 30 16 * * * /srv/www/mopa-utils/jobs/check_if_answers_were_received.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
0 17 * * * /srv/www/mopa-utils/jobs/send_daily_report.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
# 15 17 * * * /srv/www/mopa-utils/jobs/send_daily_survey_replies.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
30 17 * * 7 /srv/www/mopa-utils/jobs/send_weekly_report.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
30 18 1 * * /srv/www/mopa-utils/jobs/send_monthly_report.sh >> /srv/www/mopa-utils/mopa/data/logs/jobs.log 2>&1
```
