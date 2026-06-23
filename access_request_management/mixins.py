from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from utilities.exceptions import PermissionsViolation
class BlockSuperuserMixin:
    superuser_blocked_message = _("Superusers are not allowed to perform this action.")
    def dispatch(self, request, *args, **Kwargs):
        if request.user.is_superuser:
            messages.error(request, self.superuser_blocked_message)
            raise PermissionsViolation(self.superuser_blocked_message)
        return super().dispatch(request, *args, **Kwargs)

class CreatorRequiredMixin:
    creator_field = "created_by"
    creator_required_message = _("You are not allowed to modify this object.")

    def check_creator_permission(self, request, obj):
        
        creator = getattr(obj, self.creator_field, None)
        return creator == request.user

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)

        if obj.pk and not self.check_creator_permission(self.request, obj):
            messages.error(self.request, self.creator_required_message)
            raise PermissionsViolation(self.creator_required_message)

        return obj

class ViewPermissionMixin:
    creator_field = "created_by"
    view_blocked_message= _("You do not have permission to view this object.")
    def check_object_permissions(self, request, obj):
        if request.user.is_superuser:
            return True
        creator= getattr(obj, self.creator_field, None)
        return creator == request.user
    def get_object(self, **kwargs):
        obj= super().get_object(**kwargs)
        if obj.pk and not self.check_object_permissions(self.request, obj):
            messages.error(self.request, self.view_blocked_message)
            raise PermissionsViolation(self.view_blocked_message)
        return obj
    
class ObjectStatePermissionMixin:
    edit_blocked_message = _("You do not have permission to edit this object.")
    delete_blocked_message = _("You do not have permission to delete this object.")
    def check_object_permissions(self, obj):
        return True
    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)

        if obj.pk and not self.check_object_permissions(obj):
            message = self.edit_blocked_message
            messages.error(self.request, message)
            raise PermissionsViolation(message)

        return obj
    
class AccessRequestViewPermissionMixin(ViewPermissionMixin):
    def check_object_permissions(self, request, obj):
        if request.user.is_superuser:
            return obj.is_superuser_viewable
        return super().check_object_permissions(request, obj)

class AccessRequestEditPermissionMixin(ObjectStatePermissionMixin):
    def check_object_permissions(self, obj):
        return obj.is_editable
    

class AccessRequestDeletePermissionMixin(ObjectStatePermissionMixin):
    def check_object_permissions(self, obj):
        return obj.is_deletable

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)

        if obj.pk and not self.check_object_permissions(obj):
            message = self.delete_blocked_message
            messages.error(self.request, message)
            raise PermissionsViolation(message)

        return obj

class AccessRequestPersonEditPermissionMixin(ObjectStatePermissionMixin):
    def check_object_permissions(self, obj):
        return obj.access_request.is_editable
    def get_object(self, **kwargs):
        obj= super().get_object(**kwargs)
        if obj.pk and not self.check_object_permissions(obj):
            message = self.edit_blocked_message
            messages.error(self.request, message)
            raise PermissionsViolation(message)
        return obj

class AccessRequestPersonDeletePermissionMixin(ObjectStatePermissionMixin):
    def check_object_permissions(self, obj):
        return obj.access_request.is_deletable
    def get_object(self, **kwargs):
        obj= super().get_object(**kwargs)
        if obj.pk and not self.check_object_permissions(obj):
            message = self.delete_blocked_message
            messages.error(self.request, message)
            raise PermissionsViolation(message)
        return obj
    


    
