from django.urls import path
from django.utils.translation import gettext_lazy as _

from django_fusion.fragments.generic.actions import DeleteBulkActionView
from django_fusion.fragments.generic.base import Action
from django_fusion.fragments.forms.create import CreateModelView
from django_fusion.fragments.forms.delete import DeleteModelView
from django_fusion.fragments.generic.detail import DetailModelView
from django_fusion.fragments.forms.update import UpdateModelView
from django_fusion.contrib import DEFAULT, first_not_default, has_object_perm
from django_fusion.contrib import ViewProp as viewprop

from ..core.base import ViewsetMeta
from .base import BaseModelViewset
from ..core.sites import AppMenuMixin


class ListBulkActionsMixin(metaclass=ViewsetMeta):
	list_bulk_actions = DEFAULT

	def get_list_bulk_actions(self, request, *actions):
		if self.list_bulk_actions is not DEFAULT:
			actions = (*self.list_bulk_actions, *actions)
		return actions


class CreateViewMixin(metaclass=ViewsetMeta):
	create_view_class = CreateModelView
	create_form_layout = DEFAULT
	create_form_class = DEFAULT
	create_form_widgets = DEFAULT

	def has_add_permission(self, user):
		return has_object_perm(user, "add", self.model)

	def get_create_view_kwargs(self, **kwargs):
		view_kwargs = {
			"form_class": first_not_default(
				self.create_form_class, getattr(self, "form_class", DEFAULT)
			),
			"form_widgets": first_not_default(
				self.create_form_widgets, getattr(self, "form_widgets", DEFAULT)
			),
			"layout": first_not_default(
				self.create_form_layout, getattr(self, "form_layout", DEFAULT)
			),
			**self.create_view_kwargs,
			**kwargs,
		}
		return self.filter_kwargs(self.create_view_class, **view_kwargs)

	def get_list_page_actions(self, request, *actions):
		if self.has_add_permission(request.user):
			add_action = Action(name=_("Add new"), url=self.reverse("add"), icon="add_circle")
			actions = (add_action, *actions)
		return super().get_list_page_actions(request, *actions)

	@viewprop
	def create_view_kwargs(self):
		return {}

	@viewprop
	def create_view(self):
		return self.create_view_class.as_view(**self.get_create_view_kwargs())

	@property
	def create_path(self):
		return path("add/", self.create_view, name="add")


class UpdateViewMixin(metaclass=ViewsetMeta):
	update_view_class = UpdateModelView
	update_page_actions = DEFAULT

	update_form_layout = DEFAULT
	update_form_class = DEFAULT
	update_form_widgets = DEFAULT

	form_layout = DEFAULT
	form_class = DEFAULT
	form_widgets = DEFAULT

	def has_change_permission(self, user, obj=None):
		return has_object_perm(user, "change", self.model, obj=obj)

	def get_update_view_kwargs(self, **kwargs):
		view_kwargs = {
			"form_class": first_not_default(self.update_form_class, self.form_class),
			"form_widgets": first_not_default(self.update_form_widgets, self.form_widgets),
			"layout": first_not_default(self.update_form_layout, self.form_layout),
			**self.update_view_kwargs,
			**kwargs,
		}
		return self.filter_kwargs(self.update_view_class, **view_kwargs)

	@viewprop
	def update_view_kwargs(self):
		return {}

	@viewprop
	def update_view(self):
		return self.update_view_class.as_view(**self.get_update_view_kwargs())

	@property
	def update_path(self):
		return path("<path:pk>/change/", self.update_view, name="change")

	def get_update_page_actions(self, request, obj, *actions):
		if self.update_page_actions is not DEFAULT:
			actions = (*self.update_page_actions, *actions)
		return actions


class ModelViewset(
	ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin, AppMenuMixin, BaseModelViewset
):
	"""List/Create/Update/Delete for a model."""

	def get_object_url(self, request, obj):
		if self.has_change_permission(request.user, obj):
			return self.reverse("change", args=[obj.pk])

	def get_success_url(self, request, obj=None):
		return self.reverse("index")


class DeleteViewMixin(metaclass=ViewsetMeta):
	delete_view_class = DeleteModelView

	def has_delete_permission(self, user, obj=None):
		return has_object_perm(user, "delete", self.model, obj=obj)

	"""
    Bulk delete
    """
	bulk_delete_view_class = DeleteBulkActionView

	def get_bulk_delete_view_kwargs(self, **kwargs):
		view_kwargs = {
			"filterset_class": self.list_filterset_class,
			"filter_fields": self.list_filter_fields,
			**self.bulk_delete_view_kwargs,
			**kwargs,
		}
		return self.filter_kwargs(self.bulk_delete_view_class, **view_kwargs)

	@viewprop
	def bulk_delete_view_kwargs(self):
		return {}

	@viewprop
	def bulk_delete_view(self):
		return self.bulk_delete_view_class.as_view(**self.get_bulk_delete_view_kwargs())

	@property
	def bulk_delete_path(self):
		return path("action/delete/", self.bulk_delete_view, name="bulk_delete")

	def get_list_bulk_actions(self, request, *actions):
		if self.has_delete_permission(request.user):
			bulk_delete_action = Action(
				name="Delete selected objects", url=self.reverse("bulk_delete"), icon="delete"
			)
			actions = (bulk_delete_action, *actions)
		return super().get_list_bulk_actions(request, *actions)

	"""
    Delete single object
    """

	def get_delete_view_kwargs(self, **kwargs):
		view_kwargs = {**self.delete_view_kwargs, **kwargs}
		return self.filter_kwargs(self.delete_view_class, **view_kwargs)

	@viewprop
	def delete_view_kwargs(self):
		return {}

	@viewprop
	def delete_view(self):
		return self.delete_view_class.as_view(**self.get_delete_view_kwargs())

	@property
	def delete_path(self):
		return path("<path:pk>/delete/", self.delete_view, name="delete")

	def get_update_page_actions(self, request, obj, *actions):
		if self.has_delete_permission(request.user):
			actions = (
				Action(name="Delete", url=self.reverse("delete", args=[obj.pk]), icon="delete"),
				*actions,
			)
		return super().get_update_page_actions(request, obj, *actions)


class DetailViewMixin(metaclass=ViewsetMeta):
	def get_object_url(self, request, obj):
		if self.has_view_permission(request.user, obj):
			return self.reverse("detail", args=[obj.pk])

	def get_success_url(self, request, obj=None):
		if obj is not None and obj.pk is not None:
			return self.reverse("detail", args=[obj.pk])
		return self.reverse("index")

	"""
    Detail
    """
	detail_view_class = DetailModelView
	detail_page_actions = DEFAULT
	detail_page_object_actions = DEFAULT

	def get_detail_view_kwargs(self, **kwargs):
		view_kwargs = {**self.detail_view_kwargs, **kwargs}
		return self.filter_kwargs(self.detail_view_class, **view_kwargs)

	@viewprop
	def detail_view_kwargs(self):
		return {}

	@viewprop
	def detail_view(self):
		return self.detail_view_class.as_view(**self.get_detail_view_kwargs())

	@property
	def detail_path(self):
		return path("<path:pk>/detail/", self.detail_view, name="detail")

	def get_detail_page_actions(self, request, obj, *actions):
		if hasattr(self, "has_delete_permission") and self.has_delete_permission(
			request.user, obj=obj
		):
			actions = (
				Action(name="Delete", url=self.reverse("delete", args=[obj.pk]), icon="delete"),
				*actions,
			)
		if self.detail_page_actions is not DEFAULT:
			actions = (*self.detail_page_actions, *actions)
		return actions

	def get_detail_page_object_actions(self, request, obj, *actions):
		if self.detail_page_object_actions is not DEFAULT:
			return (*self.detail_page_object_actions, *actions)
		return actions


class ReadonlyModelViewset(DetailViewMixin, ListBulkActionsMixin, AppMenuMixin, BaseModelViewset):
	"""
	Readonly model viewset with List and object details view only
	"""
