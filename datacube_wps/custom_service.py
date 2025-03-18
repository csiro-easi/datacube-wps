from pywps import Service
from typing import Dict, Optional, Sequence

from .custom_response import MyDescribeResponse


class MyService(Service):
    """
    A custom Service class to use a custom DescribeResponse class.
    """
    def __init__(self, processes: Sequence = [], cfgfiles=None, preprocessors: Optional[Dict] = None):
        super().__init__(processes, cfgfiles, preprocessors)

    def describe(self, wps_request, uuid, identifiers):
        """
        Override base implementation to use custom DescribeResponse class.
        """
        response_cls = MyDescribeResponse
        return response_cls(wps_request, uuid, processes=self.processes,
                            identifiers=identifiers)