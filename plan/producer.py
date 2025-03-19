import pika
import json

def send_to_queue(document, operation):
    message = {
        'operation': operation,
        'document': document
    }
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='index_queue')
    channel.basic_publish(exchange='', routing_key='index_queue', body=json.dumps(message))
    connection.close()
