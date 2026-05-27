"""
Navigation menu items for access_request_management.

For more information on navigation menus, see:
https://docs.netbox.dev/en/stable/plugins/development/navigation/
"""

from netbox.plugins.navigation import PluginMenu
from netbox.plugins import PluginMenuButton, PluginMenuItem
from django.utils.translation import gettext_lazy as _
menu= PluginMenu(
    label=_("Security Control"),
    groups=(
        (
            _("Management"),
            (
                PluginMenuItem(
                    link="plugins:access_request_management:accessrequest_list",
                    link_text=_("Access Request Management"),
                    permissions=[
                        # "access_request_management.view_accessrequest"
                    ],
                    buttons= (
                        PluginMenuButton(
                            link="plugins:access_request_management:accessrequest_add",
                            title=_("Add"),
                            icon_class="mdi mdi-plus-thick",
                            permissions=[
                                "access_request_management.add_accessrequest"
                            ],
                        ),
                    ),
                ),
            ),
        ),
    ),
)