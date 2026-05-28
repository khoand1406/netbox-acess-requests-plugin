from collections import defaultdict
import json
import logging
import os
from pathlib import Path
import shutil
from urllib.parse import unquote

from django.utils.translation import gettext_lazy as _
from django.db import transaction, router
from django.contrib import messages
from django.http import JsonResponse, QueryDict
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from extras.ui.panels import TagsPanel
from netbox import settings
from netbox.object_actions import AddObject, BulkDelete, BulkEdit, BulkImport, DeleteObject, EditObject
from netbox.ui.layout import SimpleLayout
from netbox.ui.panels import RelatedObjectsPanel
from netbox.views import generic
from utilities.exceptions import AbortRequest, PermissionsViolation
from utilities.forms.utils import restrict_form_fields
from utilities.views import ViewTab, register_model_view
from . import models, tables, forms, filtersets
from .ui.panels import AccessRequestPanel, AccessRequestPersonPanel, CustomImageAttachmentPanel
from .bulk_import_forms import AccessRequestPersonBulkImportCSVForm
from django.contrib.contenttypes.prefetch import GenericPrefetch
from upload_file_plugin.models import UploadedFile
from upload_file_plugin.views import SaveFilesView

def get_member_list_count(instance):
    try:
        return models.AccessRequestPerson.objects.filter(
        access_request= instance.pk
    ).count()
    except Exception:
        return 0

class AccessRequestListView(generic.ObjectListView):
    queryset= models.AccessRequest.objects.all()
    table= tables.AccessRequestTable
    filterset= filtersets.AccessRequestFilterSet
    filterset_form= forms.AccessRequestFilterForm
    
    def get_queryset(self, request):
        
        qs = self.queryset.all()

        if request.user.is_superuser:
            qs = qs.exclude(
            status=models.AccessRequestStatusChoices.STATUS_DRAFT
        )
        else:
            qs = qs.filter(created_by=request.user)

        return qs
    def get_permitted_actions(self, user, model=None):

        actions = list(super().get_permitted_actions(user, model))

        if user.is_superuser:

            blocked_actions = (
            AddObject,
            BulkImport,
            BulkEdit,
            BulkDelete,
        )

            actions = [
            action for action in actions
            if not issubclass(action, blocked_actions)
        ]

        return actions
    
class AccessRequestView(generic.ObjectView):
    queryset= models.AccessRequest.objects.all()
    layout= SimpleLayout(
        left_panels=[
            AccessRequestPanel(),
            TagsPanel()
        ],
        right_panels=[
            RelatedObjectsPanel(),
        ]
    )
    actions= (EditObject, DeleteObject)
    def get_permitted_actions(self, user, model=None):
        instance = self.get_object(**self.kwargs)
        filtered_actions = []
        for action in self.actions:
            if action == EditObject and not instance.is_editable:
                continue
            if action == DeleteObject and not instance.is_deletable:
                continue
            filtered_actions.append(action)

        original_actions = self.actions
        self.actions = tuple(filtered_actions)
        result = super().get_permitted_actions(user, model)
        self.actions = original_actions  

        return result

    def get_extra_context(self, request, instance):
        return {
                "is_admin":(request.user.is_superuser),
                "confirmed":instance.is_confirmed,
                "submit": (instance.can_submit and not request.user.is_superuser),
                "is_approved": instance.is_approved,
                "is_rejected": instance.is_rejected,
                "is_finished":instance.is_finished,
                "is_editable": instance.is_editable,
                "is_deletable": instance.is_deletable,
        }

@register_model_view(model= models.AccessRequest, name="access-members", path="access-members")
class AccessRequestPersonListView(generic.ObjectView):
    queryset= models.AccessRequest.objects.all()
    template_name= 'access_request_management/access_member_list.html'
    tab= ViewTab(
        label=_('Members List'),
        badge= get_member_list_count,
        weight=500
    )
    def get_extra_context(self, request, instance):
        members = (
            models.AccessRequestPerson.objects
            .filter(access_request_id=instance.pk)
        )
        model_name = models.AccessRequestPerson._meta.model_name
        member_ids = [m.pk for m in members]

        attachments_qs = UploadedFile.objects.filter(
            model_name=model_name,
            object_id__in=member_ids
        )

        attachments_map = defaultdict(list)
        for f in attachments_qs:
            attachments_map[f.object_id].append(f)
            
        for member in members:
            member.prefetched_attachments = attachments_map.get(member.pk, [])
    
        return {
            "is_superuser":(request.user.is_superuser),
            "approved": instance.is_approved,
            "confirmed":instance.is_confirmed,
            "members": members
        }

@register_model_view(model=models.AccessRequest, name="request-history", path='request-history')
class AccessRequestHistoryListView(generic.ObjectView):
    queryset= models.AccessRequest.objects.all()
    template_name= 'access_request_management/access_request_history.html'
    
    tab= ViewTab(
        label=_('Request History')
    )
    def get_extra_context(self, request, instance):
        request_history= models.AccessRequestHistory.objects.filter(access_request_id= instance.pk)
        return {
            "request_history": request_history
        }

class AccessRequestEditView(generic.ObjectEditView):
    queryset=models.AccessRequest.objects.all()
    form= forms.AccessRequestForm
    def alter_object(self, obj, request, url_args, url_kwargs):
        if not obj.pk:
            obj.created_by = request.user
        return obj
    

class AccessRequestDeleteView(generic.ObjectDeleteView):
    queryset= models.AccessRequest.objects.all()
    
class AccessRequestPersionListView(generic.ObjectListView):
    queryset= models.AccessRequestPerson.objects.all()
    table= tables.AccessRequestPersonTable
    filterset= filtersets.AccessRequestPersonFilterSet
    filterset_form= forms.AccessRequestPersonFilterForm

class AccessRequestPersonView(generic.ObjectView):
    queryset = models.AccessRequestPerson.objects.all()
    layout = SimpleLayout(
        left_panels=[
            AccessRequestPersonPanel(),
            TagsPanel()
        ],
        right_panels=[
            CustomImageAttachmentPanel()
        ]
    )
    actions = (EditObject, DeleteObject)

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        self._current_instance = instance

        actions = self.get_permitted_actions(request.user, model=instance)

        return render(request, self.get_template_name(), {
            'object': instance,
            'actions': actions,
            'tab': self.tab,
            'layout': self.layout,
            **self.get_extra_context(request, instance),
        })

    def get_permitted_actions(self, user, model=None):
        permitted = super().get_permitted_actions(user, model)
        instance = getattr(self, '_current_instance', None)
        if instance is None:
            return permitted

        access_request = instance.access_request
        is_approved = access_request.is_approved

        result = []
        for action in permitted:
            if action == EditObject and is_approved:
                continue
            if action == DeleteObject and is_approved:
                continue 
            result.append(action)

        return result

class AccessRequestPersonEditView(generic.ObjectEditView):
    queryset= models.AccessRequestPerson.objects.all()
    form= forms.AccessRequestPersonForm
    def alter_object(self, obj, request, url_args, url_kwargs):
        return super().alter_object(obj, request, url_args, url_kwargs)
    
    def post(self, request, *args, **kwargs):
        logger = logging.getLogger('netbox.views.ObjectEditView')
        obj = self.get_object(**kwargs)
        model = self.queryset.model
        if obj.pk and hasattr(obj, 'snapshot'):
            obj.snapshot()

        obj = self.alter_object(obj, request, args, kwargs)

        form_prefix = 'quickadd' if request.GET.get('_quickadd') else None
        form = self.form(data=request.POST, files=request.FILES, instance=obj, prefix=form_prefix)
        restrict_form_fields(form, request.user)
        if form.is_valid():
            logger.debug("Form validation was successful")
            obj._changelog_message = form.cleaned_data.pop('changelog_message', '')

            try:
                with transaction.atomic(using=router.db_for_write(model)):
                    object_created = form.instance.pk is None
                    obj = form.save()
        
                    all_files = request.POST.get("all_files", "[]")
        
                    if all_files and all_files.strip() != "[]":
                        temp_data = QueryDict(mutable=True)
                        temp_data.update({
                            "all_files": all_files,
                            "model_name": obj._meta.model_name,
                            "object_id": str(obj.pk)
                        })
            
                        original_data = getattr(request, "_data", None)
                        request.data = temp_data
            
                        try:
                            save_view = SaveFilesView()
                            result = save_view.post(request)
                            result_data = json.loads(result.content)
                
                            if not result_data.get("success"):
                                raise AbortRequest(
                                f"Failed to save attachments: {result_data.get('errors')}"
                            )
                
                            saved_files = result_data.get("saved_files", [])
                
                            for file_info in saved_files:
                                old_relative = unquote(file_info["path"].lstrip("/"))
                                media_root_name = Path(settings.MEDIA_ROOT).name

                                if old_relative.startswith(f"{media_root_name}/"):
                                    old_relative = old_relative[len(media_root_name) + 1:]
                                old_full = os.path.join(settings.MEDIA_ROOT, old_relative)

                                file_name = os.path.basename(old_relative)
                                new_relative = os.path.join("uploads", obj._meta.model_name, file_name)
                                new_full = os.path.join(settings.MEDIA_ROOT, new_relative)
                    
                                os.makedirs(os.path.dirname(new_full), exist_ok=True)
                    
                                if os.path.exists(old_full):
                                    shutil.move(old_full, new_full)
                                    logger.info(f"Moved file: {old_full} -> {new_full}")
                                    UploadedFile.objects.filter(
                                    object_id=obj.pk,
                                    model_name=obj._meta.model_name,
                                    file=file_name
                                ).update(file=new_relative)
                                    logger.info(f"Updated DB path: {file_name} -> {new_relative}")
                                else:
                                    logger.warning(f"File not found after save: {old_full}")
                
                        
                            all_files_list = json.loads(all_files)
                            allowed_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'tmp')
                
                            for file_dict in all_files_list:
                                temp_path = file_dict.get("path", "")
                                abs_temp_path = os.path.abspath(temp_path)
                    
                                if not abs_temp_path.startswith(os.path.abspath(allowed_dir)):
                                    logger.warning(f"Invalid temp path, skipping: {temp_path}")
                                    continue
                    
                                if os.path.exists(abs_temp_path):
                                    try:
                                        os.remove(abs_temp_path)
                                        logger.info(f"Deleted temp file: {abs_temp_path}")
                                    except Exception as e:
                                        logger.error(f"Error deleting temp file {abs_temp_path}: {e}")
                            
                        finally:
                            if original_data is not None:
                                request.data = original_data
                            elif hasattr(request, "data"):
                                del request.data
                        
                msg = '{} {}'.format(
                    'Created' if object_created else 'Modified',
                    self.queryset.model._meta.verbose_name
                )
                logger.info(f"{msg} {obj} (PK: {obj.pk})")
                if hasattr(obj, 'get_absolute_url'):
                    msg = mark_safe(f'{msg} <a href="{obj.get_absolute_url()}">{escape(obj)}</a>')
                else:
                    msg = f'{msg} {obj}'
                messages.success(request, msg)

                
                if '_quickadd' in request.POST:
                    return render(request, 'htmx/quick_add_created.html', {
                        'object': obj,
                    })

                
                if '_addanother' in request.POST:
                    redirect_url = request.path
                    return redirect(redirect_url)

                return_url = self.get_return_url(request, obj)

                # HTMX
                if request.htmx:
                    from django.http import HttpResponse
                    return HttpResponse(headers={'HX-Location': return_url})

                return redirect(return_url)

            except (AbortRequest, PermissionsViolation, ValidationError) as e:
                logger.debug(e.message)
                form.add_error(None, e.message)

        else:
            logger.debug("Form validation failed")

        context = {
            'model': model,
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            **self.get_extra_context(request, obj),
        }

        if '_quickadd' in request.POST:
            return render(request, 'htmx/quick_add.html', context)

        return render(request, self.template_name, context)

class AccessRequestPersonDeleteView(generic.ObjectDeleteView):
    queryset= models.AccessRequestPerson.objects.all()
    
class AccessRequestPersionImportView(generic.BulkImportView):
    queryset= models.AccessRequestPerson.objects.all()
    model_form= AccessRequestPersonBulkImportCSVForm
    def save_object(self, object_form, request):
        obj = object_form.save(commit=False)
        if obj.pk is None and hasattr(obj, 'created_by'):
            obj.created_by = request.user
        obj.save()
        object_form.save_m2m()
        return obj
    
        
