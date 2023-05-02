# GetCapabilities request
curl http://localhost:8000/?request=GetCapabilities&service=WPS

# GetCapabilities response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- PyWPS 4.5.2 -->
<wps:Capabilities service="WPS" version="1.0.0" xml:lang="en-US" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsGetCapabilities_response.xsd" updateSequence="1">
    <ows:ServiceIdentification>
        <ows:Title>CSIRO EASI WPS</ows:Title>
        <ows:Abstract>CSIRO EASI WPS Service</ows:Abstract>
        <ows:Keywords>
        <ows:Keyword>WPS</ows:Keyword>
        <ows:Keyword>GRASS</ows:Keyword>
        <ows:Keyword>PyWPS</ows:Keyword>
            <ows:Type codeSpace="ISOTC211/19115">theme</ows:Type>
        </ows:Keywords>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
        <ows:ServiceTypeVersion>2.0.0</ows:ServiceTypeVersion>
        <ows:Fees>None</ows:Fees>
        <ows:AccessConstraints>
        None
        </ows:AccessConstraints>
    </ows:ServiceIdentification>
    <ows:ServiceProvider>
        <ows:ProviderName>CSIRO</ows:ProviderName>
        <ows:ProviderSite xlink:href="http://www.csiro.au"/>
        <ows:ServiceContact>
            <ows:IndividualName>CSIRO EASI</ows:IndividualName>
            <ows:PositionName>Organization</ows:PositionName>
            <ows:ContactInfo>
                <ows:Phone>
                    <ows:Voice>+xx-xxx-xxx-xxxx</ows:Voice>
                    <ows:Facsimile/>
                </ows:Phone>
                <ows:Address>
                    <ows:DeliveryPoint/>
                    <ows:City>Canberra</ows:City>
                    <ows:AdministrativeArea/>
                    <ows:PostalCode>2601</ows:PostalCode>
                    <ows:Country>Australia</ows:Country>
                    <ows:ElectronicMailAddress>robert.woodcock@csiro.au</ows:ElectronicMailAddress>
                </ows:Address>
            </ows:ContactInfo>
        </ows:ServiceContact>
    </ows:ServiceProvider>
    <ows:OperationsMetadata>
        <ows:Operation name="GetCapabilities">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://localhost:8000"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="DescribeProcess">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://localhost:8000"/>
                    <ows:Post xlink:href="http://localhost:8000"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="Execute">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://localhost:8000"/>
                    <ows:Post xlink:href="http://localhost:8000"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
    </ows:OperationsMetadata>
    <wps:ProcessOfferings>
        <wps:Process wps:processVersion="0.4">
            <ows:Identifier>WOfSDrill</ows:Identifier>
            <ows:Title>Water Observations from Space Pixel Drill</ows:Title>
            <ows:Abstract>Water Observations from Space Pixel Drill

Water Observations from Space (WOfS) provides surface water observations derived from satellite imagery for all of Australia. The current product (Version 2.1.5) includes observations taken from 1986 to the present, from the Landsat 5, 7 and 8 satellites. WOfS covers all of mainland Australia and Tasmania but excludes off-shore Territories.

The WOfS product allows users to get a better understanding of where water is normally present in a landscape, where water is seldom observed, and where inundation has occurred occasionally.

This Pixel Drill will output the water observations for a point through time as graph.

For service status information, see https://status.dea.ga.gov.au.
</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="0.3">
            <ows:Identifier>FractionalCoverDrill</ows:Identifier>
            <ows:Title>Fractional Cover</ows:Title>
            <ows:Abstract>Performs Fractional Cover Polygon Drill</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="0.2">
            <ows:Identifier>Mangrove Cover Drill</ows:Identifier>
            <ows:Title>Mangrove Cover</ows:Title>
            <ows:Abstract>Performs Mangrove Polygon Drill</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="0.2">
            <ows:Identifier>WIT</ows:Identifier>
            <ows:Title>WIT</ows:Title>
            <ows:Abstract>WIT polygon drill</ows:Abstract>
        </wps:Process>
    </wps:ProcessOfferings>
    <wps:Languages>
        <wps:Default>
            <ows:Language>en-US</ows:Language>
        </wps:Default>
        <wps:Supported>
            <ows:Language>en-US</ows:Language>
        </wps:Supported>
    </wps:Languages>
</wps:Capabilities>
```


# DescribeProcess request
curl 'http://localhost:8000/?service=WPS&request=DescribeProcess&version=1.0.0&Identifier=Mangrove%20Cover%20Drill'

# DescribeProcess response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- PyWPS 4.5.2 -->
<wps:ProcessDescriptions xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsDescribeProcess_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US">
    <ProcessDescription wps:processVersion="0.2" storeSupported="true" statusSupported="true">
        <ows:Identifier>Mangrove Cover Drill</ows:Identifier>
        <ows:Title>Mangrove Cover</ows:Title>
        <ows:Abstract>Performs Mangrove Polygon Drill</ows:Abstract>
        <DataInputs>
            <Input minOccurs="1" maxOccurs="1">
                <ows:Identifier>geometry</ows:Identifier>
                <ows:Title>Geometry</ows:Title>
                <ows:Abstract></ows:Abstract>
                <ComplexData maximumMegabytes="1">
                    <Default>
                        <Format>
                            <MimeType>application/vnd.geo+json</MimeType>
                            <Schema>http://geojson.org/geojson-spec.html#polygon</Schema>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>application/vnd.geo+json</MimeType>
                            <Schema>http://geojson.org/geojson-spec.html#polygon</Schema>
                        </Format>
                    </Supported>
                </ComplexData>
            </Input>
            <Input minOccurs="1" maxOccurs="1">
                <ows:Identifier>start</ows:Identifier>
                <ows:Title>Start Date</ows:Title>
                <ows:Abstract></ows:Abstract>
                <ComplexData maximumMegabytes="1">
                    <Default>
                        <Format>
                            <MimeType>application/vnd.geo+json</MimeType>
                            <Schema>http://www.w3.org/TR/xmlschema-2/#dateTime</Schema>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>application/vnd.geo+json</MimeType>
                            <Schema>http://www.w3.org/TR/xmlschema-2/#dateTime</Schema>
                        </Format>
                    </Supported>
                </ComplexData>
            </Input>
            <Input minOccurs="1" maxOccurs="1">
                <ows:Identifier>end</ows:Identifier>
                <ows:Title>End date</ows:Title>
                <ows:Abstract></ows:Abstract>
                <ComplexData maximumMegabytes="1">
                    <Default>
                        <Format>
                            <MimeType>application/vnd.geo+json</MimeType>
                            <Schema>http://www.w3.org/TR/xmlschema-2/#dateTime</Schema>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>application/vnd.geo+json</MimeType>
                            <Schema>http://www.w3.org/TR/xmlschema-2/#dateTime</Schema>
                        </Format>
                    </Supported>
                </ComplexData>
            </Input>
        </DataInputs>
        <ProcessOutputs>
            <Output>
                <ows:Identifier>timeseries</ows:Identifier>
                <ows:Title>Timeseries Drill</ows:Title>
                <ows:Abstract></ows:Abstract>
                <ComplexOutput>
                    <Default>
                        <Format>
                            <MimeType>application/vnd.terriajs.catalog-member+json</MimeType>
                            <Encoding>utf-8</Encoding>
                            <Schema>https://tools.ietf.org/html/rfc7159</Schema>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>application/vnd.terriajs.catalog-member+json</MimeType>
                            <Encoding>utf-8</Encoding>
                            <Schema>https://tools.ietf.org/html/rfc7159</Schema>
                        </Format>
                    </Supported>
                </ComplexOutput>
            </Output>
        </ProcessOutputs>
    </ProcessDescription>
</wps:ProcessDescriptions>
```

# Execute request
```xml
<?xml version="1.0" encoding="UTF-8"?>
<wps:Execute version="1.0.0" service="WPS" xml:lang="en-US" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wps/1.0.0" xmlns:wfs="http://www.opengis.net/wfs" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:wcs="http://www.opengis.net/wcs/1.1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsDescribeProcess_response.xsd">
  <ows:Identifier>Mangrove Cover Drill</ows:Identifier>
  <wps:DataInputs>
    <wps:Input>
      <ows:Identifier>geometry</ows:Identifier>
      <wps:Data>
        <wps:ComplexData mimeType="application/vnd.geo+json"><![CDATA[{"features": [{"geometry": {"type": "Polygon", "coordinates": [[[153.1, -27.4], [153.3, -27.4], [153.3, -27.2], [153.1, -27.2], [153.1, -27.4]]]}, "crs": "EPSG:4326"}]}]]></wps:ComplexData>
      </wps:Data>
    </wps:Input>
    <wps:Input>
      <ows:Identifier>start</ows:Identifier>
      <wps:Data>
        <wps:ComplexData mimeType="application/vnd.geo+json"><![CDATA[{"properties": {"timestamp": {"date-time": "2019-01-01"}}}]]></wps:ComplexData>
      </wps:Data>
    </wps:Input>
    <wps:Input>
      <ows:Identifier>end</ows:Identifier>
      <wps:Data>
        <wps:ComplexData mimeType="application/vnd.geo+json"><![CDATA[{"properties": {"timestamp": {"date-time": "2019-03-01"}}}]]></wps:ComplexData>
      </wps:Data>
    </wps:Input>
  </wps:DataInputs>
  <wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/vnd.terriajs.catalog-member+json">
      <ows:Identifier>timeseries</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
</wps:Execute>
```

# Execute response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US" serviceInstance="http://localhost:8000?request=GetCapabilities&amp;amp;service=WPS" statusLocation="http://localhost:8000/outputs/ae111cfe-e87a-11ed-a5c0-0242ac120003.xml">
    <wps:Process wps:processVersion="0.2">
        <ows:Identifier>Mangrove Cover Drill</ows:Identifier>
        <ows:Title>Mangrove Cover</ows:Title>
        <ows:Abstract>Performs Mangrove Polygon Drill</ows:Abstract>
	</wps:Process>
    <wps:Status creationTime="2023-05-01T23:48:33Z">
        <wps:ProcessSucceeded>PyWPS Process Mangrove Cover finished</wps:ProcessSucceeded>
	</wps:Status>
	<wps:ProcessOutputs>
		<wps:Output>
            <ows:Identifier>timeseries</ows:Identifier>
            <ows:Title>Timeseries Drill</ows:Title>
            <ows:Abstract></ows:Abstract>
			<wps:Data>
                    <wps:ComplexData mimeType="application/vnd.terriajs.catalog-member+json" encoding="utf-8" schema="https://tools.ietf.org/html/rfc7159"><![CDATA[{"data": "time,Woodland,Open Forest,Closed Forest\n2019-07-02,0,38,144\n", "isEnabled": true, "type": "csv", "name": "Mangrove Cover", "tableStyle": {"columns": {"Woodland": {"units": "#", "chartLineColor": "#9FFF4C", "active": true}, "Open Forest": {"units": "#", "chartLineColor": "#5ECC00", "active": true}, "Closed Forest": {"units": "#", "chartLineColor": "#3B7F00", "active": true}}}}]]></wps:ComplexData>
			</wps:Data>
		</wps:Output>
	</wps:ProcessOutputs>
</wps:ExecuteResponse>
```

# Terria wwwroot/init/simple.json configuration
```json
{
  "homeCamera": {
    "north": -8,
    "east": 158,
    "south": -45,
    "west": 109
  },
  "catalog": [
    {
      "id": "ZIdekvc10z",
      "type": "wms-group",
      "name": "Test",
      "url": "https://programs.communications.gov.au/geoserver/ows",
      "members": [
        {
          "type": "wms",
          "localId": "mybroadband%3AMyBroadband_ADSL_Availability",
          "legends": [
            {
              "items": [
                {
                  "title": "A - Best",
                  "color": "#6B0038"
                },
                {
                  "title": "B",
                  "color": "#F41911"
                },
                {
                  "title": "C",
                  "color": "#F67F00"
                },
                {
                  "title": "D",
                  "color": "#D78B6D"
                },
                {
                  "title": "E - Worst",
                  "color": "#ECD2BE"
                },
                {
                  "title": "No data",
                  "color": "rgba(0,0,0,0)",
                  "outlineColor": "black",
                  "addSpacingAbove": true
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "Mangrove Cover Drill",
      "type": "wps",
      "storeSupported": true,
      "statusSupported": true,
      "url": "http://localhost:8000/?service=WPS",
      "identifier": "Mangrove Cover Drill",
      "forceConvertResultsToV8": true
    },
    {
      "id": "Water Observations From Space Drill",
      "type": "wps",
      "storeSupported": true,
      "statusSupported": true,
      "url":"https://wps.dev.easi-eo.solutions/?service=WPS",
      "identifier": "WOfSDrill",
      "forceConvertResultsToV8": true
    },
    {
      "id": "Fractional Cover Drill",
      "type": "wps",
      "storeSupported": true,
      "statusSupported": true,
      "url":"https://wps.dev.easi-eo.solutions/?service=WPS",
      "identifier": "FractionalCoverDrill",
      "forceConvertResultsToV8": true
    },
    {
      "id": "WIT Polygon Drill",
      "type": "wps",
      "storeSupported": true,
      "statusSupported": true,
      "url":"https://wps.dev.easi-eo.solutions/?service=WPS",
      "identifier": "WIT",
      "forceConvertResultsToV8": true
    }
  ],
  "viewerMode": "3dSmooth",
  "baseMaps": {
    "defaultBaseMapId": "basemap-positron",
    "previewBaseMapId": "basemap-positron"
  },
  "corsDomains": [ 
    "localhost:8000",
    "localhost:5000",
    "https://s3.ap-southeast-2.amazonaws.com",
    "s3.ap-southeast-2.amazonaws.com"
  ]
}
```