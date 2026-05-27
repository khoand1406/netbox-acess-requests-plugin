from typing import Any

from django import forms
from upload_file_plugin.models import UploadedFile
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data: Any, initial: Any | None = None) -> Any:
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [super(MultipleFileField, self).clean(d, initial) for d in data]
        return [super(MultipleFileField, self).clean(data, initial)]

class CustomUploadWidget(MultipleFileInput):
    template_name = "upload_file/upload.html"

    def __init__(self, *args, **kwargs):
        self.instance = None
        super().__init__(*args, **kwargs)

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        ctx = super().get_context(name, value, attrs)
        ctx["widget"]["object_id"] = attrs.get("object_id", "") if attrs else ""
        ctx["widget"]["model_name"] = attrs.get("model_name", "") if attrs else ""

        if self.instance and self.instance.pk:
            ctx["uploaded_files"] = UploadedFile.objects.filter(
                object_id=self.instance.pk,
                model_name=self.instance._meta.model_name
            )
        else:
            ctx["uploaded_files"] = []

        return ctx