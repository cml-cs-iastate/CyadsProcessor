# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ProcessorAddsViaExtension(models.Model):
    attempt = models.IntegerField()
    capturetimestamp = models.DateTimeField(db_column='captureTimeStamp', blank=True, null=True)  # Field name made lowercase.
    ad_source = models.CharField(max_length=65, blank=True, null=True)
    ad_skip_duration = models.IntegerField()
    ad_system = models.CharField(max_length=65, blank=True, null=True)
    ad_video_id = models.CharField(max_length=65, blank=True, null=True)
    batch_id = models.IntegerField()
    botid = models.IntegerField(db_column='botId')  # Field name made lowercase.
    video_watched_id = models.CharField(max_length=65)
    session_guid = models.CharField(max_length=40, blank=True, null=True)
    user_id = models.CharField(max_length=256, blank=True, null=True)
    blk_unblk = models.IntegerField(blank=True, null=True)
    ip = models.CharField(db_column='IP', max_length=256, blank=True, null=True)  # Field name made lowercase.
    other = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    processed = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'processor_adds_via_extension'
