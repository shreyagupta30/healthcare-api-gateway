from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django_redis import get_redis_connection
from rest_framework import status
from plan.serializers import PlanSerializer
import json
from datetime import date
import hashlib
from rest_framework import serializers
from .producer import send_to_queue

redis_conn = get_redis_connection("default")

CACHE_KEY = 'plans'

class PlanViewSet(ViewSet):
    serializer_class = PlanSerializer

    def check_bearer_token(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {
                    "message": "Authorization token missing or invalid",
                    "status_code": 401
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        return None

    def generate_etag(self, data):
        data_json = json.dumps(data)
        etag = hashlib.md5(data_json.encode('utf-8')).hexdigest()
        return f'W/"{etag}"'

    def list(self, request):
        auth_response = self.check_bearer_token(request)
        if auth_response:
            return auth_response

        plans = redis_conn.hgetall(CACHE_KEY)
        plans_data = {}
        for key, value in plans.items():
            plan_data = json.loads(value)
            plans_data[key.decode('utf-8')] = plan_data
        return Response(plans_data)

    def retrieve(self, request, pk):
        auth_response = self.check_bearer_token(request)
        if auth_response:
            return auth_response

        if not pk:
            return Response(
                {
                    "message": "Plan ID not provided",
                    "status_code": 400
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        plan = redis_conn.hget(CACHE_KEY, pk)
        if plan:
            plan_data = json.loads(plan)
            weak_etag = self.generate_etag(plan_data)

            if_none_match = request.headers.get('If-None-Match')
            if if_none_match == weak_etag:
                return Response(status=status.HTTP_304_NOT_MODIFIED)

            if_match = request.headers.get('If-Match')
            if if_match and if_match != weak_etag:
                return Response(
                    {
                        "message": "Precondition Failed",
                        "status_code": 412
                    },
                    status=status.HTTP_412_PRECONDITION_FAILED
                )

            response = Response(plan_data)
            response['ETag'] = weak_etag
            return response
        else:
            return Response(
                {
                    "message": "Plan not found",
                    "status_code": 404
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        auth_response = self.check_bearer_token(request)
        if auth_response:
            return auth_response

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Missing or invalid fields in request body",
                    "status_code": 400,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Convert date objects to strings
        for key, value in validated_data.items():
            if isinstance(value, date):
                validated_data[key] = value.isoformat()

        object_id = validated_data['objectId']
        if redis_conn.hexists(CACHE_KEY, object_id):
            return Response(
                {
                    "message": f"Plan with ID: {object_id} already exists",
                    "status_code": 409
                },
                status=status.HTTP_409_CONFLICT
            )

        weak_etag = self.generate_etag(validated_data)
        redis_conn.hset(CACHE_KEY, object_id, json.dumps(validated_data))
        send_to_queue(validated_data, 'create')  # Send create operation to RabbitMQ

        response = Response(
            {
                "message": f"Plan with ID: {object_id} saved",
                "status_code": 201
            },
            status=status.HTTP_201_CREATED
        )
        response['ETag'] = weak_etag
        return response

    def update(self, request, pk=None):
        auth_response = self.check_bearer_token(request)
        if auth_response:
            return auth_response

        if not pk:
            return Response(
                {
                    "message": "Plan ID not provided",
                    "status_code": 400
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        plan = redis_conn.hget(CACHE_KEY, pk)
        if not plan:
            return Response(
                {
                    "message": "Plan not found",
                    "status_code": 404
                },
                status=status.HTTP_404_NOT_FOUND
            )

        plan_data = json.loads(plan)
        weak_etag = self.generate_etag(plan_data)

        if_match = request.headers.get('If-Match')
        if if_match and if_match != weak_etag:
            return Response(
                {
                    "message": "Precondition Failed",
                    "status_code": 412
                },
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Missing or invalid fields in request body",
                    "status_code": 400,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Convert date objects to strings
        for key, value in validated_data.items():
            if isinstance(value, date):
                validated_data[key] = value.isoformat()

        weak_etag = self.generate_etag(validated_data)
        redis_conn.hset(CACHE_KEY, pk, json.dumps(validated_data))
        send_to_queue(validated_data, 'update')  # Send update operation to RabbitMQ

        response = Response(
            {
                "message": f"Plan with ID: {pk} updated",
                "status_code": 200
            },
            status=status.HTTP_200_OK
        )
        response['ETag'] = weak_etag
        return response

    def partial_update(self, request, pk):
        auth_response = self.check_bearer_token(request)
        if auth_response:
            return auth_response

        if not pk:
            return Response(
                {
                    "message": "Plan ID not provided",
                    "status_code": 400
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        plan = redis_conn.hget(CACHE_KEY, pk)
        if not plan:
            return Response(
                {
                    "message": "Plan not found",
                    "status_code": 404
                },
                status=status.HTTP_404_NOT_FOUND
            )

        plan_data = json.loads(plan)
        weak_etag = self.generate_etag(plan_data)

        if_match = request.headers.get('If-Match')
        if if_match and if_match != weak_etag:
            return Response(
                {
                    "message": "Precondition Failed",
                    "status_code": 412
                },
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        serializer = self.serializer_class(plan_data, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Missing or invalid fields in request body",
                    "status_code": 400,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Convert date objects to strings
        for key, value in validated_data.items():
            if isinstance(value, date):
                validated_data[key] = value.isoformat()

        # Handle unique key constraint for planCostShares["objectId"]
        if 'planCostShares' in validated_data:
            plan_cost_shares_data = validated_data['planCostShares']
            if 'objectId' in plan_cost_shares_data and plan_cost_shares_data['objectId'] != plan_data['planCostShares']['objectId']:
                raise serializers.ValidationError({
                    'planCostShares': {
                        'objectId': 'Updating objectId is not allowed.'
                    }
                })

        # Compare and add new linkedPlanServices
        if 'linkedPlanServices' in validated_data:
            existing_services = plan_data.get('linkedPlanServices', [])
            incoming_services = validated_data['linkedPlanServices']

            # Convert existing services to a set of tuples for easy comparison
            existing_services_set = {tuple(sorted((k, tuple(v.items())) if isinstance(v, dict) else (k, v) for k, v in service.items())) for service in existing_services}

            for service_data in incoming_services:
                service_tuple = tuple(sorted((k, tuple(v.items())) if isinstance(v, dict) else (k, v) for k, v in service_data.items()))
                if service_tuple not in existing_services_set:
                    # Add the new service data to the existing list
                    existing_services.append(service_data)
    
            validated_data['linkedPlanServices'] = existing_services

        plan_data.update(validated_data)
        weak_etag = self.generate_etag(plan_data)

        redis_conn.hset(CACHE_KEY, pk, json.dumps(plan_data))
        send_to_queue(plan_data, 'update')  # Send update operation to RabbitMQ

        response = Response(
            {
                "message": f"Plan with ID: {pk} partially updated",
                "status_code": 200
            },
            status=status.HTTP_200_OK
        )
        response['ETag'] = weak_etag
        return response

    def destroy(self, request, pk):
        auth_response = self.check_bearer_token(request)
        if auth_response:
            return auth_response

        if not pk:
            return Response(
                {
                    "message": "Plan ID not provided",
                    "status_code": 400
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        plan = redis_conn.hget(CACHE_KEY, pk)
        if not plan:
            return Response(
                {
                    "message": "Plan not found",
                    "status_code": 404
                },
                status=status.HTTP_404_NOT_FOUND
            )

        plan_data = json.loads(plan)
        weak_etag = self.generate_etag(plan_data)

        if_match = request.headers.get('If-Match')
        if if_match and if_match != weak_etag:
            return Response(
                {
                    "message": "Precondition Failed",
                    "status_code": 412
                },
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        if_not_match = request.headers.get('If-None-Match')
        if if_not_match and if_not_match == weak_etag:
            return Response(
                {
                    "message": "Precondition Failed",
                    "status_code": 412
                },
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        redis_conn.hdel(CACHE_KEY, pk)
        send_to_queue(plan_data, 'delete')  # Send delete operation to RabbitMQ
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
