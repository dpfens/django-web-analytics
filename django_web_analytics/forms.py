from django import forms
from webanalytics import models


class BaseMixin(forms.ModelForm):

    class Meta:
        exclude = ['is_internal', 'created_at', 'created_by', 'last_modified_at', 'last_modified_by', 'deleted_at', 'deleted_by']


class PrivacyForm(BaseMixin):

    class Meta:
        model = models.Privacy
        exclude = BaseMixin.Meta.exclude + ['user']
