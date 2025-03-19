from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import MemberCostShare, Service, PlanService, Plan

@registry.register_document
class MemberCostShareDocument(Document):
    class Index:
        name = 'member_cost_shares'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = MemberCostShare
        fields = [
            'deductible',
            '_org',
            'copay',
            'objectId',
            'objectType',
        ]

@registry.register_document
class ServiceDocument(Document):
    class Index:
        name = 'services'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Service
        fields = [
            '_org',
            'objectId',
            'objectType',
            'name',
        ]

@registry.register_document
class PlanServiceDocument(Document):
    linkedService = fields.ObjectField(properties={
        '_org': fields.TextField(),
        'objectId': fields.TextField(),
        'objectType': fields.TextField(),
        'name': fields.TextField(),
    })
    planserviceCostShares = fields.ObjectField(properties={
        'deductible': fields.IntegerField(),
        '_org': fields.TextField(),
        'copay': fields.IntegerField(),
        'objectId': fields.TextField(),
        'objectType': fields.TextField(),
    })

    class Index:
        name = 'plan_services'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = PlanService
        fields = [
            '_org',
            'objectId',
            'objectType',
        ]

@registry.register_document
class PlanDocument(Document):
    planCostShares = fields.ObjectField(properties={
        'deductible': fields.IntegerField(),
        '_org': fields.TextField(),
        'copay': fields.IntegerField(),
        'objectId': fields.TextField(),
        'objectType': fields.TextField(),
    })
    linkedPlanServices = fields.NestedField(properties={
        'linkedService': fields.ObjectField(properties={
            '_org': fields.TextField(),
            'objectId': fields.TextField(),
            'objectType': fields.TextField(),
            'name': fields.TextField(),
        }),
        'planserviceCostShares': fields.ObjectField(properties={
            'deductible': fields.IntegerField(),
            '_org': fields.TextField(),
            'copay': fields.IntegerField(),
            'objectId': fields.TextField(),
            'objectType': fields.TextField(),
        }),
        '_org': fields.TextField(),
        'objectId': fields.TextField(),
        'objectType': fields.TextField(),
    })

    class Index:
        name = 'plans'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Plan
        fields = [
            '_org',
            'objectId',
            'objectType',
            'planType',
            'creationDate',
        ]
