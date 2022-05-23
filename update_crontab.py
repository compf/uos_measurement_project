from crontab import CronTab
import sys
import json
def main(path:str):
    with open(path) as f:
        json_obj=json.load(f)
        interval=json_obj["interval"]
        root_dir=json_obj["root_dir"]
        cron=CronTab()
        jobs=cron.find_command("measurement_script")
        if len(job)>0:
            job=jobs[0]
        else:
            job=cron.new("cd " +root_dir +" && " + "./measurement_script.sh")
        job.minute.every(interval)
        cron.write()

