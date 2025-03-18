from pywps.response.describe import DescribeResponse

import pywps.configuration as config
from pywps.app.basic import get_json_indent, get_response_type, make_response


class MyDescribeResponse(DescribeResponse):
    """
    A custom DescribeResponse class to change the XML output for process descriptions.
    This is required to mimic the GSKY WPS service's 'Any' DataType tags so as to work
    with TerriaJS and get the Point/Polygon/Existing custom user-interface for services.
    """

    def __init__(self, wps_request, uuid, **kwargs):
        super().__init__(wps_request, uuid, **kwargs)

    def _construct_doc(self):
        """
        Override base implementation to modify the ows:DataType tag to remove the reference type info
        when empty.
        """
        if not self.identifiers:
            raise MissingParameterValue('Missing parameter value "identifier"', 'identifier')

        doc = self.json
        json_response, mimetype = get_response_type(
            self.wps_request.http_request.accept_mimetypes, self.wps_request.default_mimetype)
        if json_response:
            doc = json.dumps(self._render_json_response(doc), indent=get_json_indent())
        else:
            template = self.template_env.get_template(self.version + '/describe/main.xml')
            max_size = int(config.get_size_mb(config.get_config_value('server', 'maxsingleinputsize')))
            doc = template.render(max_size=max_size, **doc)

        # CHANGE FROM PARENT IMPLEMENTATION:
        # If no datatype set on DataType tag, replace partial reference attribute value with an empty string.
        doc = doc.replace('<ows:DataType ows:reference="http://www.w3.org/TR/xmlschema-2/#"></ows:DataType>', '<ows:DataType ows:reference=""></ows:DataType>')

        return doc, mimetype
