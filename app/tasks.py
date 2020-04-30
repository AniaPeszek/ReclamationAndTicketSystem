import json
import sys
import csv
import os
import io
import re
from rq import get_current_job
from app import create_app, db
from app.models import Task, User, Ticket
from app.email import send_email
from flask import render_template
from datetime import datetime
from flask_mail import Message
from app import mail


app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress',
                                    {'task_id': job.get_id(), 'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_report(user_id, json_data):
    try:
        user = User.query.get(user_id)
        
        _set_task_progress(0)
        
        data = json_data['table']
        address = json_data['mail']
        if not validate_email(address):
            raise ValueError('Invalid email address')

        _set_task_progress(10)
        msg = Message('ERP - Your report from ERP application',
                    sender=app.config['ADMINS'][0], recipients=[address])
        msg.body=render_template('email/export_report.txt', user=user)
        msg.html=render_template('email/export_report.html', user=user)

        _set_task_progress(50)

        # create csv file in memory
        headers=data['header']
        body=data['body']
        report = io.StringIO()
        cw = csv.writer(report)
        cw.writerow(headers)
        cw.writerows(body)
        filename=''.join(['report_', user.username,'.csv'])
        _set_task_progress(75)
        msg.attach(filename, "text/csv", report.getvalue())

        mail.send(msg)
        _set_task_progress(100)


    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)