import pika


def handle_event(event_type, event_id):
    # Define what to do based on the event type and ID
    if event_type == "rmq_created":
        print(f"Handling created event for ID: {event_id}")
    elif event_type == "rmq_updated":
        print(f"Handling updated event for ID: {event_id}")
    else:
        print(f"Unknown event type: {event_type} for ID: {event_id}")

def callback(ch, method, properties, body):
    message = body.decode('utf-8')
    print(f"Received: {message}")
    
    # Parse the XML message to extract the event type and ID
    import xml.etree.ElementTree as ET
    root = ET.fromstring(message)
    event_type = root.find('type').text
    event_id = root.find('data/id').text
    
    # Handle the event based on the type and ID
    handle_event(event_type, event_id)

def subscribe():
    try:
        # Connect to RabbitMQ with credentials
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq',
            credentials=pika.PlainCredentials('user', 'password')  # Use the credentials set in docker-compose.yml
        ))
        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue='test_queue')

        # Set up subscription
        channel.basic_consume(queue='test_queue', on_message_callback=callback, auto_ack=True)

        print("Subscriber started...")
        channel.start_consuming()
    except Exception as e:
        print(f"Error in subscriber: {e}")

if __name__ == "__main__":
    subscribe()
