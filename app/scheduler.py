from datetime import datetime
from logging import info

from flask_apscheduler import APScheduler

from app import Sessions, Users, app
from app.universal import global_delete_user, global_get_users

# Scheduler
schedule = APScheduler()
schedule.init_app(app)
schedule.start()

# Scheduled tasks
@schedule.task('interval', id='checkExpiringUsers', minutes=15, misfire_grace_time=900)
def check_expiring_users():
    info('Checking for expiring users...')
    # Get all users that have an expiration date set and are expired
    expiring = Users.select().where(Users.expires < datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Delete all expired users
    for user in expiring:
        global_delete_user(user)
        info(f"Deleting user { user.email if user.email else user.username } due to expired invite.")
        
@schedule.task('interval', id='scanUsers', minutes=30, misfire_grace_time=900)
def scan_users():
    info('Scanning for new users...')
    # Get all new users
    global_get_users()
    
@schedule.task('interval', id='scanLibraries', minutes=30, misfire_grace_time=900)
def scan_libraries():
    info('Scanning for new libraries...')
    # Get all new libraries


def get_schedule():
    job_store = schedule.get_jobs()
    
    schedule_list = []
    
    for job in job_store:
        # Replace underscores with spaces and capitalize first letter of each word
        name = job.name.replace("_", " ").title()
        
        schedule_info = {
            'id': job.id,
            'name': name,
            'trigger': str(job.trigger),
            'next_run_time': str(job.next_run_time)
        }
        
        schedule_list.append(schedule_info)
    
    return schedule_list

def get_task(job_id):
    job_store = schedule.get_job(id=job_id)
    
    schedule_info = {
        'id': job_store.id,
        'name': job_store.name,
        'trigger': str(job_store.trigger),
        'next_run_time': str(job_store.next_run_time)
    }
    
    return schedule_info

def run_task(job_id):
    return schedule.modify_job(id=job_id, jobstore=None, next_run_time=datetime.now())