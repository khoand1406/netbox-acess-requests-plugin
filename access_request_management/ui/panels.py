from netbox.ui.panels import Panel
from netbox.ui import panels, attrs
from django.utils.translation import gettext_lazy as _
from upload_file_plugin.models import UploadedFile
class AccessRequestPanel(panels.ObjectAttributesPanel):

    name = _("Detail Information")
    slug = "access_request_details"

    name_attr = attrs.TextAttr(
        "name",
        label=_("Name")
    )

    status_attr = attrs.ChoiceAttr(
        "status",
        label=_("Status")
    )

    planned_date_attr = attrs.TextAttr(
        "planned_date",
        label=_("Planned Date")
    )

    reason_attr = attrs.TextAttr(
        "reason",
        label=_("Reason")
    )

    region_attr = attrs.RelatedObjectAttr(
        "region",
        linkify=True,
        label=_("Region")
    )

    site_attr = attrs.RelatedObjectAttr(
        "site",
        linkify=True,
        label=_("Site")
    )

    # created_by_attr = attrs.RelatedObjectAttr(
    #     "created_by",
    #     linkify=True,
    #     label=_("Created By")
    # )

    # created_attr = attrs.DateTimeAttr(
    #     "created",
    #     label=_("Created")
    # )

    # last_updated_attr = attrs.DateTimeAttr(
    #     "last_updated",
    #     label=_("Last Updated")
    # )
    
class AccessRequestPersonPanel(panels.ObjectAttributesPanel):
    name = _("Detail Information")
    slug = "access_request_details"
    name_attr= attrs.TextAttr("full_name", label= _("Full Name"))
    code= attrs.TextAttr("identity_code", label= _("Identity Code"))
    
    organization= attrs.TextAttr("organization")
    job_title= attrs.TextAttr("job_title")
    phone_number= attrs.TextAttr("phone_number")
    location= attrs.RelatedObjectAttr("location", linkify= True)
    status_attr = attrs.ChoiceAttr(
        "status",
        label=_("Status")
    )
    description= attrs.TextAttr("description")
    
class CustomImageAttachmentPanel(Panel):
    title= _("Attachments")
    template_name= "access_request_management/panels/custom_attachments_panel.html"
    
    def get_context(self, context):
        obj= context["object"]
        request= context["request"]
        uploaded_files= UploadedFile.objects.filter(
            model_name= obj._meta.model_name,
            object_id= obj.pk
        ).order_by("-created_at")
        can_delete_attachment= (not request.user.is_superuser and obj.is_editable)
        return {
            **super().get_context(context),
            "uploaded_files": uploaded_files,
            "object": obj,
            "model_name":obj._meta.model_name,
            "can_delete_attachment": can_delete_attachment,
        }
    