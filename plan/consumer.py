import pika
import json
from elasticsearch import Elasticsearch

# Initialize the Elasticsearch client
es = Elasticsearch(
    hosts=[{
        'host': 'localhost',
        'port': 9200,
        'scheme': 'http'
    }],
    basic_auth=('elastic', 'BuZWUREG')
)

# Define the index settings and mappings
index_name = 'plans'
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "my_join_field": {
                "type": "join",
                "relations": {
                    "plan": ["planCostShares", "linkedPlanServices"],
                    "linkedPlanServices": ["linkedService", "planserviceCostShares"]
                }
            },
            "planCostShares": {
                "properties": {
                    "deductible": {"type": "integer"},
                    "_org": {"type": "text"},
                    "copay": {"type": "integer"},
                    "objectId": {"type": "text"},
                    "objectType": {"type": "text"}
                }
            },
            "linkedPlanServices": {
                "properties": {
                    "linkedService": {
                        "properties": {
                            "_org": {"type": "text"},
                            "objectId": {"type": "text"},
                            "objectType": {"type": "text"},
                            "name": {"type": "text"}
                        }
                    },
                    "planserviceCostShares": {
                        "properties": {
                            "deductible": {"type": "integer"},
                            "_org": {"type": "text"},
                            "copay": {"type": "integer"},
                            "objectId": {"type": "text"},
                            "objectType": {"type": "text"}
                        }
                    },
                    "_org": {"type": "text"},
                    "objectId": {"type": "text"},
                    "objectType": {"type": "text"}
                }
            },
            "_org": {"type": "text"},
            "objectId": {"type": "text"},
            "objectType": {"type": "text"},
            "planType": {"type": "text"},
            "creationDate": {"type": "date", "format": "yyyy-MM-dd"}
        }
    }
}

# Create the index with the defined settings and mappings
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_settings)

def index_document(document, parent_id=None):
    object_id = document.get('objectId')
    if parent_id:
        es.index(index=index_name, id=object_id, body=document, routing=parent_id)
    else:
        es.index(index=index_name, id=object_id, body=document)

# In plan/producer.py
def delete_document(object_id):
    # Delete all child documents of type 'planCostShares'
    query_planCostShares = {
        "query": {
            "parent_id": {
                "type": "planCostShares",
                "id": object_id
            }
        }
    }
    es.delete_by_query(index='plans', body=query_planCostShares)

    # Delete all child documents of type 'linkedPlanServices'
    query_linkedPlanServices = {
        "query": {
            "parent_id": {
                "type": "linkedPlanServices",
                "id": object_id
            }
        }
    }
    es.delete_by_query(index='plans', body=query_linkedPlanServices)

    # Retrieve IDs of 'linkedPlanServices' documents
    response = es.search(index='plans', body=query_linkedPlanServices, _source=False)
    linked_service_ids = [hit['_id'] for hit in response['hits']['hits']]

    for service_id in linked_service_ids:
        # Delete 'linkedService' documents
        query_linkedService = {
            "query": {
                "parent_id": {
                    "type": "linkedService",
                    "id": service_id
                }
            }
        }
        es.delete_by_query(index='plans', body=query_linkedService)

        # Delete 'planserviceCostShares' documents
        query_planserviceCostShares = {
            "query": {
                "parent_id": {
                    "type": "planserviceCostShares",
                    "id": service_id
                }
            }
        }
        es.delete_by_query(index='plans', body=query_planserviceCostShares)

    # Delete the parent 'plan' document
    es.delete(index='plans', id=object_id)

def callback(ch, method, properties, body):
    message = json.loads(body)
    operation = message['operation']
    document = message['document']
    object_id = document.get('objectId')
    
    if operation == 'delete':
        delete_document(object_id)
    else:
        document['my_join_field'] = {"name": "plan"}
        index_document(document)
        
        # Index planCostShares
        plan_cost_shares = document.get('planCostShares')
        if plan_cost_shares:
            plan_cost_shares['my_join_field'] = {"name": "planCostShares", "parent": document['objectId']}
            index_document(plan_cost_shares, parent_id=document['objectId'])
        
        # Index linkedPlanServices
        linked_plan_services = document.get('linkedPlanServices', [])
        for service in linked_plan_services:
            service['my_join_field'] = {"name": "linkedPlanServices", "parent": document['objectId']}
            index_document(service, parent_id=document['objectId'])
            
            # Index linkedService
            linked_service = service.get('linkedService')
            if linked_service:
                linked_service['my_join_field'] = {"name": "linkedService", "parent": service['objectId']}
                index_document(linked_service, parent_id=service['objectId'])
            
            # Index planserviceCostShares
            planservice_cost_shares = service.get('planserviceCostShares')
            if planservice_cost_shares:
                planservice_cost_shares['my_join_field'] = {"name": "planserviceCostShares", "parent": service['objectId']}
                index_document(planservice_cost_shares, parent_id=service['objectId'])

    print(f" [x] Processed {operation} operation for document with ID {object_id}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='index_queue')
channel.basic_consume(queue='index_queue', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
