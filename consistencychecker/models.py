from django.db import models


class Consistency(models.Model):
    date = models.DateField("Fecha")
    profile_file = models.IntegerField()
    profile_index = models.IntegerField()
    speed_file = models.IntegerField()
    speed_index = models.IntegerField()
    bip_file = models.IntegerField()
    bip_index = models.IntegerField()
    odbyroute_file = models.IntegerField()
    odbyroute_index = models.IntegerField()
    trip_file = models.IntegerField()
    trip_index = models.IntegerField()
    paymentfactor_file = models.IntegerField()
    paymentfactor_index = models.IntegerField()
    general_file = models.IntegerField()
    general_index = models.IntegerField()
    authority_period_version = models.CharField()
