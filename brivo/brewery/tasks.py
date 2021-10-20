from django.contrib.auth import get_user_model
from celery.schedules import crontab
from brivo.brewery.models import (
    Batch,
)
from brivo.utils import functions

from config import celery_app

User = get_user_model()
users = User.objects.all()


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    for user in users:
        print(f"Adding celery task for {user}")
        sender.add_periodic_task(
            crontab(minute=0, hour=18),
            check_fermenting_batches.s(user.username, user.email),
            name=f"{user} batch check",
        )


@celery_app.task()
def check_fermenting_batches(user, email):
    """A pointless Celery task to demonstrate usage."""
    print(f"Checking batches for {user}")
    batches = Batch.objects.filter(user__username=user)
    for batch in batches:

        if batch.stage not in ["PRIMARY_FERMENTATION", "SECONDARY_FERMENTATION"]:
            continue
        ndays = batch.get_ndays_since_brewing()
        if ndays < 7:
            # print(f" - {batch.name} is fermenting for less than a week")
            pass
        elif ndays == 7:
            functions.send_mail(
                template="brewery/emails/batch_fermentation.html",
                subject=f"{{batch.name}} is fermenting for {ndays}",
                email=email,
                context={
                    "ndays": ndays,
                    "name": batch.name,
                    "batch_number": batch.batch_number,
                    "username": user,
                },
            )
        elif ndays == 14:
            functions.send_mail(
                template="brewery/emails/batch_fermentation.html",
                subject=f"{{batch.name}} is fermenting for {ndays}",
                email=email,
                context={
                    "ndays": ndays,
                    "name": batch.name,
                    "batch_number": batch.batch_number,
                    "username": user,
                },
            )
        elif ndays > 30:
            # print(f" - {batch.name} is fermenting for a long time")
            pass
        else:
            pass