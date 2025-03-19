from django.db import models

class MemberCostShare(models.Model):
    deductible = models.IntegerField()
    _org = models.CharField(max_length=255)
    copay = models.IntegerField()
    objectId = models.CharField(max_length=255)
    objectType = models.CharField(max_length=255)

class Service(models.Model):
    _org = models.CharField(max_length=255)
    objectId = models.CharField(max_length=255)
    objectType = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

class PlanService(models.Model):
    linkedService = models.ForeignKey(Service, on_delete=models.CASCADE)
    planserviceCostShares = models.ForeignKey(MemberCostShare, on_delete=models.CASCADE)
    _org = models.CharField(max_length=255)
    objectId = models.CharField(max_length=255)
    objectType = models.CharField(max_length=255)

class Plan(models.Model):
    planCostShares = models.ForeignKey(MemberCostShare, on_delete=models.CASCADE)
    linkedPlanServices = models.ManyToManyField(PlanService)
    _org = models.CharField(max_length=255)
    objectId = models.CharField(max_length=255)
    objectType = models.CharField(max_length=255)
    planType = models.CharField(max_length=255)
    creationDate = models.DateField()
