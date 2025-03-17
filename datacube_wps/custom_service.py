from pywps import Service
from typing import Dict, Optional, Sequence

from .custom_response import MyDescribeResponse


class MyService(Service):
    def __init__(self, processes: Sequence = [], cfgfiles=None, preprocessors: Optional[Dict] = None):
        super().__init__(processes, cfgfiles, preprocessors)

    def describe(self, wps_request, uuid, identifiers): # Override describe
        response_cls = MyDescribeResponse
        #response.get_response("describe")
        return response_cls(wps_request, uuid, processes=self.processes,
                            identifiers=identifiers)