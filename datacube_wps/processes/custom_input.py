from pywps import LiteralInput
from pywps.inout.literaltypes import AnyValue


class AnyValueInput(LiteralInput):
    """
    Custom input that accepts any type of data and modifies its JSON to work with
    the custom DescribeResponse class to ensure the desired XML output is created.
    """
    def __init__(self, *args, **kwargs):
        """
        Force set some properties to ensure Input is 'Any'.
        """
        kwargs["allowed_values"] = AnyValue()
        kwargs["data_type"] = ""
        super(AnyValueInput, self).__init__(*args, **kwargs)

    @property
    def json(self):
        """
        Override parent function to force set JSON values to ensure Input is 'Any'.
        """
        default_json = super().json
        default_json["data_type"] = ""
        default_json["allowed_values"]: [{"type": "anyvalue"}]
        return default_json