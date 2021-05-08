from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _


User = get_user_model()


class BaseModel(models.Model):
    """
    A table for storing generic timestamp information about an object
    """
    is_internal = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    last_modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)
    deleted_at = models.DateTimeField(db_index=True, blank=True, null=True)

    class Meta:
        abstract = True


class LookupModel(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField()

    def __str__(self):
        return _(self.name)

    class Meta:
        abstract = True
        ordering = ('name', )


class Privacy(BaseModel):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    opt_out_tracking = models.BooleanField(default=False)  # do not track web page views
    opt_out_event_tracking = models.BooleanField(default=False)  # do not web page events
    is_private = models.BooleanField(default=False)  # do not allow anyone to view this user's information/data or their entity's information/data


class Browser(BaseModel):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    major_version = models.PositiveSmallIntegerField()
    minor_version = models.PositiveSmallIntegerField(blank=True, null=True)
    build_maintenance_version = models.PositiveSmallIntegerField(blank=True, null=True)
    revision_build_version = models.PositiveSmallIntegerField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = (('name', 'version'),)


class BrowserFeature(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class BrowserFeatures(BaseModel):
    analytics_browser = models.ForeignKey(Browser, models.DO_NOTHING)
    analytics_browser_feature = models.ForeignKey(BrowserFeature, models.DO_NOTHING)
    supported = models.BooleanField()

    class Meta:
        unique_together = (('analytics_browser', 'analytics_browser_feature'),)


class Manufacturer(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class Device(BaseModel):
    id = models.SmallAutoField(primary_key=True)
    device_type = models.ForeignKey('DeviceType', models.DO_NOTHING)
    manufacturer = models.ForeignKey(Manufacturer, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = (('device_type', 'manufacturer', 'name'),)


class DeviceType(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class IpAddress(BaseModel):
    id = models.BigAutoField(primary_key=True)
    ip_address_type = models.ForeignKey('IpAddressType', models.DO_NOTHING)
    value = models.GenericIPAddressField()

    class Meta:
        unique_together = (('ip_address_type', 'value'),)


class IpAddressType(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class OperatingSystem(BaseModel):
    manufacturer = models.ForeignKey(Manufacturer, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=25)
    major_version = models.PositiveIntegerField(blank=True, null=True)
    minor_version = models.PositiveIntegerField(blank=True, null=True)
    build_maintenance_version = models.PositiveIntegerField(blank=True, null=True)
    revision_build_version = models.PositiveIntegerField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = (('manufacturer', 'name'),)


class Referrer(BaseModel):
    id = models.BigAutoField(primary_key=True)
    referrer_type = models.ForeignKey('ReferrerType', models.DO_NOTHING)
    value = models.CharField(max_length=250)

    class Meta:
        unique_together = (('referrer_type', 'value'),)


class ReferrerType(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class Request(BaseModel):
    id = models.BigAutoField(primary_key=True)
    request_type = models.ForeignKey('RequestType', on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    referrer = models.ForeignKey(Referrer, blank=True, null=True, on_delete=models.DO_NOTHING)
    method = models.ForeignKey('RequestMethod', on_delete=models.DO_NOTHING)
    ip_address = models.ForeignKey(IpAddress, on_delete=models.DO_NOTHING)
    device = models.ForeignKey(Device, blank=True, null=True, on_delete=models.DO_NOTHING)
    browser = models.ForeignKey(Browser, blank=True, null=True, on_delete=models.DO_NOTHING)
    url = models.ForeignKey('Url', on_delete=models.DO_NOTHING)
    user_agent = models.ForeignKey('UserAgent', on_delete=models.DO_NOTHING)
    is_ajax = models.BooleanField()
    requested_at = models.DateTimeField()


class Session(BaseModel):
    id = models.BigAutoField(primary_key=True)
    first_request_at = models.DateTimeField()
    last_request_at = models.DateTimeField()
    requests = models.ManyToManyField(Request)


class RequestFeature(BaseModel):
    request = models.ForeignKey(Request, models.DO_NOTHING)
    feature = models.ForeignKey(BrowserFeature, models.DO_NOTHING)
    supported = models.BooleanField()

    class Meta:
        unique_together = (('request', 'feature'),)


class RequestHeader(BaseModel):
    type = models.ForeignKey('RequestHeaderType', models.DO_NOTHING)
    name = models.CharField(unique=True, max_length=50)


class RequestHeaderType(BaseModel):
    name = models.CharField(unique=True, max_length=50)


class RequestHeaderValue(BaseModel):
    header = models.ForeignKey(RequestHeader, on_delete=models.DO_NOTHING)
    value = models.CharField(max_length=250)

    class Meta:
        unique_together = (('header', 'value'),)


class RequestHeaderValues(BaseModel):
    request = models.ForeignKey(Request, on_delete=models.DO_NOTHING)
    header_value = models.ForeignKey(RequestHeaderValue, on_delete=models.DO_NOTHING)


class RequestMethod(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class RequestType(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class Url(BaseModel):
    id = models.BigAutoField(primary_key=True)
    value = models.URLField(unique=True)


class UrlParameter(BaseModel):
    name = models.CharField(unique=True, max_length=25)


class UrlParameterValue(BaseModel):
    id = models.BigAutoField(primary_key=True)
    parameter = models.ForeignKey(UrlParameter, on_delete=models.DO_NOTHING)
    value = models.CharField(max_length=100)

    class Meta:
        unique_together = (('parameter', 'value'),)


class UrlParameterValues(BaseModel):
    id = models.BigAutoField(primary_key=True)
    request = models.ForeignKey(Request, on_delete=models.DO_NOTHING)
    parameter_value = models.ForeignKey(UrlParameterValue, on_delete=models.DO_NOTHING)


class UserAgent(BaseModel):
    value = models.CharField(unique=True, max_length=250)


class PerformanceEntryType(LookupModel, BaseModel):
    id = models.SmallAutoField(primary_key=True)


class PerformanceEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500, db_index=True)
    entry_type = models.ForeignKey(PerformanceEntryType, on_delete=models.CASCADE)
    start_time = models.FloatField()
    duration = models.FloatField()
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
