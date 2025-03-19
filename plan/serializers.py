from rest_framework import serializers

class StrictIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if not isinstance(data, int):
            self.fail('invalid', input=data)
        return super().to_internal_value(data)

class StrictStringField(serializers.CharField):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid', input=data)
        return super().to_internal_value(data)

class MemberCostShareSerializer(serializers.Serializer):
    deductible = StrictIntegerField()
    _org = StrictStringField()
    copay = StrictIntegerField()
    objectId = StrictStringField()
    objectType = StrictStringField()

class ServiceSerializer(serializers.Serializer):
    _org = StrictStringField()
    objectId = StrictStringField()
    objectType = StrictStringField()
    name = StrictStringField()

class PlanServiceSerializer(serializers.Serializer):
    linkedService = ServiceSerializer()
    planserviceCostShares = MemberCostShareSerializer()
    _org = StrictStringField()
    objectId = StrictStringField()
    objectType = StrictStringField()

class PlanSerializer(serializers.Serializer):
    planCostShares = MemberCostShareSerializer()
    linkedPlanServices = PlanServiceSerializer(many=True)
    _org = StrictStringField()
    objectId = StrictStringField()
    objectType = StrictStringField()
    planType = StrictStringField()
    creationDate = serializers.DateField(input_formats=["%d-%m-%Y"])
