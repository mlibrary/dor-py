import pika
import time

def publish_message(message):
    try:
        # Connect to RabbitMQ with credentials
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq',
            credentials=pika.PlainCredentials('user', 'password') 
        ))
        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue='test_queue')

        # Publish the message
        channel.basic_publish(exchange='', routing_key='test_queue', body=message)
        print(f"Sent: {message}")

        connection.close()
    except Exception as e:
        print(f"Error publishing message: {e}")

if __name__ == "__main__":
    print("Publisher starting...")
    for i in range(1, 6):  # Send 5 messages
        xml_message = f'<event><type>rmq_created</type><data><id>{i}</id></data></event>'
        publish_message(xml_message)
        xml_message = f'<event><type>rmq_updated</type><data><id>{i}</id></data></event>'
        publish_message(xml_message)
        time.sleep(5)  
    xml_message = f'<event><type>rmq_unknown</type><data><id>{i}</id></data></event>'
    publish_message(xml_message)    
    time.sleep(5)  
    print("All messages sent.")
