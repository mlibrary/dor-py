import redis
import xml.etree.ElementTree as ET

def handle_event(event_type, event_data):
    if event_type == 'redis_created':
        print(f"Handling redis created event for ID: {event_data['id']}")
    else:
        print(f"No handler for event type: {event_type}")

def main():
    print("Subscriber starting...")

    r = redis.Redis(host='redis', port=6379)
    print('Waiting for messages...')

    while True:
        message = r.brpop('test_queue')[1].decode() 
        print(f"Received: {message}")
        root = ET.fromstring(message)
        event_type = root.find('type').text
        event_data = {child.tag: child.text for child in root.find('data')}
        handle_event(event_type, event_data)

if __name__ == "__main__":
    main()
