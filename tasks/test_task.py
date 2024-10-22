import time
from random import randrange

import dramatiq

from tasks.broker import DramatiqRabbitmqBroker

QUEUE_NAME = "sleep"

BROKER = DramatiqRabbitmqBroker.from_env()
BROKER.set_up_queue(QUEUE_NAME)

@dramatiq.actor(queue_name=QUEUE_NAME)
def sleep_and_say_hi() -> None:
    sleep_period = randrange(1, 10)
    time.sleep(sleep_period)
    print(f"Hi, I slept {sleep_period} seconds!")
