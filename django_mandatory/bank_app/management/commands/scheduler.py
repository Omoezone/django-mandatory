import schedule
import time
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bank_app.models import Customer, Rank
from django.utils import timezone


class Command(BaseCommand):
    def handle(self, **options):
        self.schedule_update_rank()


    def update_rank(self):
        print('Checking for customers that should have their rank updated')
        rank_silver = Rank.objects.get(pk=4)
        one_day_ago = timezone.now() - timezone.timedelta(days=1)
        #one_month_ago = datetime.now() - relativedelta(months=1)
        customers = Customer.objects.filter(user__date_joined__gte=one_day_ago, rank__value=10)
        for customer in customers:
            print(f"Updating customer rank for {customer.user.username}")
            customer.rank = rank_silver
            customer.save()


    def schedule_update_rank(self):
        interval = 5
        schedule.every(interval).seconds.do(self.update_rank)
        #schedule.every(interval).months.do(self.update_rank)
        while True:
            schedule.run_pending()
            time.sleep(interval)