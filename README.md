# Django Web Analytics
In-house web analytics for tracking authenticated users in Django projects.

## Request Logging
To log request data in the database adding the following middleware:
```python
MIDDLEWARE = [
    ...
    'django_web_analytics.middleware.tracking.RequestLoggingMiddleware',
    ...
]
```
which will also add a `do_not_track` boolean variable to the `request` object


## Do Not Track preferences
The `do_not_track` boolean variable is specified using the optional `DNT` header.  If this header is not specified, the app will use the `django_web_analytics.models.Privacy.opt_out_tracking` boolean column.  A  `django_web_analytics.models.Privacy` instance is created whenever a new user is created.  Privacy preferences can be changed using the `django_web_analytics.forms.PrivacyForm`.  Here is a simple example:

```python
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_web_analytics.forms import PrivacyForm


class PrivacyView(View, LoginRequiredMixin):
    template_name = os.path.join('path', 'to', 'template.html')

    def get(self, request):
        privacy = request.user.privacy
        if privacy:
            form = settings_forms.PrivacyForm(instance=privacy)
        else:
            form = settings_forms.PrivacyForm()
        context = dict(form=form)
        return render(request, self.template_name, context)

    def post(self, request):
        privacy = request.user.privacy
        form = settings_forms.PrivacyForm(data=request.POST, instance=privacy)
        if form.is_valid():
            instance = form.save(commit=False)
            if not instance.user:
                instance.user = request.user
            instance.save()

        context = dict(form=form)
        return render(request, self.template_name, context)
```

### Performance Entries
The app has `django_web_analytics.models.PerformanceEntryType` and `django_web_analytics.models.PerformanceEntry` tables for recording [Performance Timeline](https://developer.mozilla.org/en-US/docs/Web/API/Performance_Timeline) data for analysis.  Here is a simple example of how to use it:
```javascript
window.addEventListener('beforeunload', function() {
  analytics.sendPerformances();
});
```
