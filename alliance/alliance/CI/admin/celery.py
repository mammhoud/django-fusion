# admin.py
from contrib.sites.admin import register
from django.contrib import admin
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
from django_celery_beat.models import (
	ClockedSchedule,
	CrontabSchedule,
	IntervalSchedule,
	PeriodicTask,
	SolarSchedule,
)
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
	pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["task"].widget = UnfoldAdminTextInputWidget()
		self.fields["regtask"].widget = UnfoldTaskSelectWidget()


@register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
	form = UnfoldPeriodicTaskForm


@register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
	pass


@register(CrontabSchedule)
class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
	pass


@register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
	pass


@register(ClockedSchedule)
class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
	pass
