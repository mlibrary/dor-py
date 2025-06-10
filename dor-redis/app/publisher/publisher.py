import redis
import time

def publish_message(message):
    r = redis.Redis(host='redis', port=6379)
    r.lpush('test_queue', message)
    print(f"Sent: {message}")

if __name__ == "__main__":
    print("Publisher starting...")
    max_messages = 5
    i = 1
    while (i <= max_messages):
        xml_message = '<event><type>redis_created</type><data><id>' + str(i) + '</id></data></event>'
        publish_message(xml_message)
        time.sleep(5)
        i += 1
        if i == max_messages:
            time.sleep(20)  #sleep before exiting so that all msg are read

    print("All messages sent. Publisher finishing.")
