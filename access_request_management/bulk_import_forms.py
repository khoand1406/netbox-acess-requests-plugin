from django.utils.translation import gettext_lazy as _
from dcim.models.sites import Location
from netbox.forms.bulk_import import PrimaryModelImportForm
from utilities.forms.fields.csv import CSVModelChoiceField
from .models import AccessRequestPerson

class AccessRequestPersonBulkImportCSVForm(PrimaryModelImportForm):
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name="name",
        required=True,
        label=_("Location"),
        help_text=_("Location")
    )
    class Meta:
        model= AccessRequestPerson
        fields= (
            "identity_code",
            "full_name",
            "organization",
            "job_title",
            "phone_number",
            "location",
            "description"
            
        )