import time
from random import randrange

import dramatiq

from tasks.broker import set_up_rabbitmq_broker

set_up_rabbitmq_broker()

@dramatiq.actor
def sleep_and_say_hi() -> None:
    sleep_period = randrange(1, 10)
    time.sleep(sleep_period)
    print(f"Hi, I slept {sleep_period} seconds!")
