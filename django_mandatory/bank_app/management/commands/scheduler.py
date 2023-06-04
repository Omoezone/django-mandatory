import schedule
import time
from bank_app.models import Customer, Rank



def update_rank():
    print('checking for customer that should have their rank updated')
    rank_silver = Rank.objects.get(pk=4)
    customers = Customer.objects.filter(rank__value=10)
    for customer in customers:
        customer.rank = rank_silver
        customer.save()


schedule.every(1).seconds.do(update_rank)


while True:
    schedule.run_pending()
    time.sleep(1)