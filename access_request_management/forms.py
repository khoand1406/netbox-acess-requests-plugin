"""
Forms for access_request_management.

For more information on NetBox forms, see:
https://docs.netbox.dev/en/stable/plugins/development/forms/
"""


from dcim.models.sites import Location, Region, Site
from netbox.forms import NetBoxModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from netbox.forms.filtersets import NetBoxModelFilterSetForm
from utilities.forms.fields.dynamic import DynamicModelChoiceField
from utilities.forms.fields.dynamic import DynamicModelMultipleChoiceField
from utilities.forms.fields.fields import TagFilterField
from utilities.forms.rendering import FieldSet
from .models import AccessRequest, AccessRequestPerson, AccessRequestPersonStatusChoices, AccessRequestStatusChoices
from .ui.widgets import MultipleFileField, CustomUploadWidget
class AccessRequestForm(NetBoxModelForm):

    planned_date = forms.DateField(
        label=_("Planned Date"),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'dd/mm/yyyy'
            }
        )
    )
    
    reason = forms.CharField(
        label=_("Reason"),
        required=True,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                'rows': 5,
            }
        )
    )
    
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required= False,
        label= _("Region")
        
    )
    
    site= DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required= False,
        label= _("Site"),
        query_params={
            "region_id": "$region"
        }
    )

    class Meta:
        model = AccessRequest

        fields = (
            'name',
            'planned_date',
            'reason',
            'region',
            'site',
            'tags',
        )

    def clean_name(self):
        """
        Validate unique request name.
        """
        name = self.cleaned_data['name']

        queryset = AccessRequest.objects.filter(name=name)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                'An access request with this name already exists.'
            )

        return name

    def clean_reason(self):
        reason = self.cleaned_data['reason']

        if len(reason) > 500:
            raise forms.ValidationError(
                'Reason cannot exceed 500 characters.'
            )

        return reason

    def clean(self):
        super().clean()

        region = self.cleaned_data.get('region')
        site = self.cleaned_data.get('site')

        if region and site and site.region_id != region.id:
            self.add_error(
            'site',
            'Selected site does not belong to selected region.'
        )

        return self.cleaned_data
    
class AccessRequestFilterForm(NetBoxModelFilterSetForm):
    model = AccessRequest
    
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by name, code, manufacturer..."),
            }
        ),
    )

    status = forms.MultipleChoiceField(
        choices=AccessRequestStatusChoices,
        required=False
    )

    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label='Region',
    )

    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        query_params={
            "region_id":"$region"
        }
    )

    planned_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date'
            }
        )
    )
    
    tag= TagFilterField(model= AccessRequest)

    fieldsets= (
        FieldSet(
            "q",
            name=_("Search"),
        ),
        FieldSet(
            "status",
            "tag",
            name=_("Basic Information"),
        ),
        FieldSet(
            "region",
            "site",
            name=_("Location Information"),
        ),
        FieldSet(
            "planned_date",
            name=_("DateTime field")
        )
    )

class AccessRequestPersonForm(NetBoxModelForm):
    
    access_request = forms.ModelChoiceField(
        queryset=AccessRequest.objects.all(),
        widget=forms.HiddenInput(),
        required=True,
    )
    site= forms.ModelChoiceField(
        queryset=Site.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )
    
    attachment = MultipleFileField(
        required=False,
        label=_("New Attachment"),
        help_text=_("Only jpg, jpeg, png allowed. Maximum total size per file: 25MB."),
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ],
        widget=CustomUploadWidget(
            attrs={
                "multiple": True
            }
        ),
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.none(),
        required=False,
        label=_("Location"),
        query_params={
            "site_id": "$site",
        },
    )

    class Meta:
        model = AccessRequestPerson
        fields = [
            "access_request",
            "identity_code",
            "site",
            "full_name",
            "organization",
            "job_title",
            "phone_number",
            "location",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        site_id = None

        if self.instance.pk and self.instance.access_request_id:
            try:
                site_id = self.instance.access_request.site_id
                self.initial["site"] = site_id
                self.initial["access_request"] = self.instance.access_request_id
            except AccessRequest.DoesNotExist:
                pass
        print(f"site_id: {site_id}")
        if not site_id:
            access_request_id = self.initial.get("access_request") or self.data.get("access_request")
            if access_request_id:
                try:
                    ar = AccessRequest.objects.get(pk=access_request_id)
                    site_id = ar.site_id
                    self.initial["site"] = site_id
                    self.initial["access_request"] = access_request_id
                except AccessRequest.DoesNotExist:
                    pass

        if site_id:
            self.fields["location"].queryset = Location.objects.filter(site_id=site_id)
        else:
            self.fields["location"].queryset = Location.objects.all()
            
        print(f"instance: {self.instance}")
        self.fields["attachment"].widget.attrs.update({
            "object_id": self.instance.pk if self.instance.pk else "",
            "model_name": self.instance._meta.model_name,
        })
        self.fields["attachment"].widget.instance = self.instance

    
    def clean_attachment(self):
        files = self.files.getlist("attachment")

        if not files:
            return []

        allowed_extensions = {"jpg", "jpeg", "png"}
        max_size = 25 * 1024 * 1024

        for file in files:
            
            if file.size > max_size:
                raise forms.ValidationError(
                    f"File '{file.name}' exceeds 25MB."
                )

            
            extension = file.name.rsplit(".", 1)[-1].lower()
            if extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"File '{file.name}' has unsupported extension."
                )

        return files    
    
    
class AccessRequestPersonFilterForm(NetBoxModelFilterSetForm):

    model = AccessRequestPerson

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
            name=_("Search"),
        ),
        FieldSet(
            "status",
            "access_request_id",
            "location_id",
            name=_("Filters"),
        ),
    )

    status = forms.MultipleChoiceField(
        required=False,
        choices=AccessRequestPersonStatusChoices,
        widget=forms.SelectMultiple,
        label=_("Status"),
    )

    access_request_id = DynamicModelMultipleChoiceField(
        queryset=AccessRequest.objects.all(),
        required=False,
        label=_("Access Request"),
    )

    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_("Location"),
    )
            