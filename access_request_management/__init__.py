"""
access_request_management

Plugin configuration for access_request_management.

For a complete list of PluginConfig attributes, see:
https://docs.netbox.dev/en/stable/plugins/development/#pluginconfig-attributes
"""

__author__ = """Khoa Nguyen"""
__email__ = "nguyenkhoa14022002@gmail.com"
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class Access_RequestConfig(PluginConfig):
    name = "access_request_management"
    verbose_name = "access_request_management"
    description = "Plugin for process access request"
    author= "Khoa Nguyen"
    author_email = "nguyenkhoa14022002@gmail.com"
    version = __version__
    base_url = "access_request_management"
    min_version = "4.5.0"
    max_version = "4.5.99"
    graphql_schema = "graphql.schema"


config = Access_RequestConfig
