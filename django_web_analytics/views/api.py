import json

from django_web_analytics import models
from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse


# Create your views here.
class PageView(View):

    def get(self, request):
        error = False
        data = dict(error=error)
        return JsonResponse(data)

    def post(self, request):
        error = False
        data = dict(error=error)
        return JsonResponse(data)


class ServiceWorkerView(View):

    def get(self, request):
        context = dict()
        return render(request, 'scripts/worker.js', context, content_type="application/x-javascript")


class AnalyticsScriptView(View):

    def get(self, request):
        context = dict()
        return render(request, 'scripts/analytics.js', context, content_type="application/x-javascript")


class EventView(View):

    def get(self, request):
        error = False
        data = dict(error=error)
        return JsonResponse(data)

    def post(self, request):
        data = json.loads(request.body)
        from pprint import pprint
        pprint(data)
        error = False
        data = dict(error=error)
        return JsonResponse(data)


class PerformanceEntryView(View):

    @staticmethod
    def create_entry(data, type_lookup):
        performance_type_name = data['entryType']

        performance_type = type_lookup.get(performance_type_name)
        if not performance_type:
            performance_type = models.PerformanceEntryType.objects.create(name=performance_type_name, description='')
            type_lookup[performance_type_name] = performance_type

        name = data.pop('name')
        start_time = data.pop('startTime', None)
        duration = data.pop('duration', 0)
        data = json.dumps(data)
        instance = models.PerformanceEntry(entry_type=performance_type, name=name, start_time= start_time, duration=duration, data=data)
        return instance

    def get(self, request):
        error = False
        data = dict(error=error)
        return JsonResponse(data)

    def post(self, request):
        data = json.loads(request.body)
        error = False
        if isinstance(data, (list, tuple, set)):

            entry_types = models.PerformanceEntryType.objects.all()
            entry_type_lookup = dict((entry_type.name, entry_type) for entry_type in entry_types)

            instances = []
            for entry in data:
                try:
                    instance = self.create_entry(entry, entry_type_lookup)
                except Exception as e:
                    error = True
                    message = repr(e)
                else:
                    instances.append(instance)
            if instances:
                models.PerformanceEntry.objects.bulk_create(instances)
                message = 'Success'
        else:
            error = True
            message = 'Must send an iterable of PerformanceEntries'
        data = dict(error=error, message=message)
        return JsonResponse(data)
