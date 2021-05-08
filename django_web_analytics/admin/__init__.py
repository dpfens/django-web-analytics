from django.contrib import admin
from django_web_analytics import models

READONLY_FIELDS = ('created_at', 'last_modified_at',)


@admin.register(models.Browser)
class BrowserAdmin(admin.ModelAdmin):
    list_display = ('name', 'version')
    readonly_fields = READONLY_FIELDS


@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'device_type')
    list_filter = ('manufacturer', 'device_type')
    readonly_fields = READONLY_FIELDS


@admin.register(models.DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = READONLY_FIELDS


@admin.register(models.RequestHeader)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ('name', 'type')
    readonly_fields = READONLY_FIELDS


@admin.register(models.RequestHeaderType)
class HeaderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = READONLY_FIELDS


@admin.register(models.IpAddressType)
class IpAddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = READONLY_FIELDS


@admin.register(models.OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'version')
    readonly_fields = READONLY_FIELDS


@admin.register(models.ReferrerType)
class ReferrerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    readonly_fields = READONLY_FIELDS


@admin.register(models.RequestMethod)
class RequestMethodAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = READONLY_FIELDS


@admin.register(models.RequestType)
class RequestTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = READONLY_FIELDS


@admin.register(models.UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    search_fields = ('name', )
