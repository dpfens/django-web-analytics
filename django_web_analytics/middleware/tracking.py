import logging
from django_web_analytics import models
import ipaddress
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        if settings.DEBUG:
            raise MiddlewareNotUsed('In DEBUG mode')

    def __call__(self, request):
        if request.path.endswith('.js') or 'api' in request.path:
            return self.get_response(request)

        request.do_not_track = request.headers.get('DNT', 0) or (request.user.is_authenticated and request.user.privacy.opt_out_tracking)
        if request.do_not_track:
            return self.get_response(request)

        now = timezone.now()

        # fetch/add method
        method = models.RequestMethod.objects.filter(name=request.method).first()
        if not method:
            method = models.RequestMethod.objects.create(name=request.method)

        # fetch/add IP Address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            raw_ip_address = x_forwarded_for.split(',')[0]
        else:
            raw_ip_address = request.META.get('REMOTE_ADDR')

        try:
            ip_address = ipaddress.ipaddress(raw_ip_address)
        except Exception:
            logger.warning('IP Address is not valid: %r', raw_ip_address)
            ip_address_type_name = 'Invalid'
        else:
            if isinstance(ip_address, ipaddress.IPv6Address):
                ip_address_type_name = 'IPv6'
            else:
                ip_address_type_name = 'IPv4'
        ip_address_type = models.IpAddressType.objects.get(name=ip_address_type_name)
        ip_address = models.IpAddress.objects.filter(ip_address_type=ip_address_type, value=raw_ip_address).first()
        if not ip_address:
            ip_address = models.IpAddress.objects.create(ip_address_type=ip_address_type, value=raw_ip_address)

        # fetch/add UserAgent
        raw_user_agent = request.META['HTTP_USER_AGENT']
        user_agent = models.UserAgent.objects.filter(value=raw_user_agent).first()
        if not user_agent:
            user_agent = models.UserAgent.objects.create(value=raw_user_agent)

        # fetch/add Device
        if request.user_agent.is_mobile:
            device_type = 'Mobile'
        elif request.user_agent.is_tablet:
            device_type = 'Tablet'
        elif request.user_agent.is_pc:
            device_type = 'PC'
        elif request.user_agent.is_bot:
            device_type = 'Bot'
        else:
            device_type = 'Unknown'

        device = request.user_agent.device
        device_family = device.family

        device_type = models.DeviceType.objects.filter(name=device_type).first()
        if not device_type:
            logger.warning('%r is not a known device type: %r', user_agent, e)
            device_type = models.DeviceType.objects.create(name=device_family, description='')

        device = models.Device.objects.filter(device_type=device_type, name=device_family).first()
        if not device:
            logger.warning('%r is not a known device_family: %r', device_family, e)
            device = models.Device.objects.create(device_type=device_type, name=device_family)

        # fetch/add Browser
        browser = models.Browser.objects.filter(name=request.user_agent.browser.family, version=request.user_agent.browser.version_string).first()
        if not browser:
            versions = dict()
            version_keys = ['major_version', 'minor_version', 'build_maintenance_version', 'revision_build_version']
            for version_type, version in zip(version_keys, request.user_agent.browser.version):
                versions[version_type] = version
            browser = models.Browser.objects.create(name=request.user_agent.browser.family, version=request.user_agent.browser.version_string, **versions)

        # fetch/add Operating System
        operating_system = models.OperatingSystem.objects.filter(name=request.user_agent.os.family, version=request.user_agent.os.version_string).first()
        if not operating_system:
            versions = dict()
            version_keys = ['major_version', 'minor_version', 'build_maintenance_version', 'revision_build_version']
            for version_type, version in zip(version_keys, request.user_agent.os.version):
                versions[version_type] = version
            operating_system = models.OperatingSystem.objects.create(name=request.user_agent.os.family, version=request.user_agent.os.version_string, **versions)

        raw_url = request.build_absolute_uri('?')
        url = models.Url.objects.filter(value=raw_url).first()
        if not url:
            url = models.Url.objects.create(value=raw_url)

        # fetch/add Referrer
        raw_referrer = request.META.get('HTTP_REFERER')
        if raw_referrer:
            referrer = models.Referrer.objects.filter(value=raw_referrer).first()
            if not referrer:
                if 'https' in raw_referrer.lower():
                    raw_referrer_type = 'HTTPS'
                else:
                    raw_referrer_type = 'HTTP'
                try:
                    referrer_type = models.ReferrerType.objects.get(name=raw_referrer_type)
                except Exception:
                    referrer_type = models.ReferrerType(name=raw_referrer_type)
                    referrer_type.save()
                referrer = models.Referrer.objects.create(value=raw_referrer, referrer_type=referrer_type)
            referrer_id = referrer.id
        else:
            referrer_id = None

        # fetch/add request type
        if request.is_secure:
            raw_request_type = 'HTTPS'
        else:
            raw_request_type = 'HTTP'
        request_type = models.RequestType.objects.filter(name=raw_request_type).first()
        if not request_type:
            request_type = models.RequestType.objects.create(name=raw_request_type, description='')

        is_ajax = request.is_ajax()
        request_instance = models.Request(request_type_id=request_type.id, user=request.user, referrer_id=referrer_id, method_id=method.id, ip_address_id=ip_address.id, device_id=device.id, browser_id=browser.id, url_id=url.id, user_agent_id=user_agent.id, is_ajax=is_ajax, requested_at=now)
        request_instance.save()

        response = self.get_response(request)
        return response
