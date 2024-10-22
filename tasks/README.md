## Task experimentation with dramatiq

Three terminals...

1. RabbitMQ

```sh
docker compose up rabbitmq
```

1. Dramatiq workers

```sh
docker compose run app bash
poetry run dramatiq tasks.test_task
```

1. Send messages

```sh
docker compose exec app bash
poetry run python
>>> from tasks.test_task import sleep_and_say_hi
>>> [sleep_and_say_hi.send() for i in range(10)]
