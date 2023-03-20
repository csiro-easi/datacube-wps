# datacube-wps
[![Scan](https://github.com/opendatacube/datacube-wps/workflows/Scan/badge.svg)](https://github.com/opendatacube/datacube-wps/actions?query=workflow%3AScan)
[![Linting](https://github.com/opendatacube/datacube-wps/workflows/Linting/badge.svg)](https://github.com/opendatacube/datacube-wps/actions?query=workflow%3ALinting)
[![Tests](https://github.com/opendatacube/datacube-wps/workflows/Tests/badge.svg)](https://github.com/opendatacube/datacube-wps/actions?query=workflow%3ATests)
[![Docker](https://github.com/opendatacube/datacube-wps/workflows/Docker/badge.svg)](https://github.com/opendatacube/datacube-wps/actions?query=workflow%3ADocker)
[![CoveCov](https://codecov.io/gh/opendatacube/datacube-wps/branch/master/graph/badge.svg)](https://codecov.io/gh/opendatacube/datacube-wps)

Datacube Web Processing Service

* Free software: Apache Software License 2.0

Datacube WPS is based on PYWPS (https://github.com/geopython/pywps) version 4.2.4

Available processes are below:
* FCDrill
* WOfSDrill

### State of play (08/12/2022)
- EASI WPS can currently run:
 - Mangrove polygon drill: Calculate number of Woodland, Open Forest and Closed Forest pixels in a polygon
 - Fractional Cover (FC) polygon drill: Calculate proportion of bare soil, photosynthetic vegetation and non-photosynthetic vegetation within a polygon.
 - Water Observations From Space (WOFS) pixel drill: Produce water observations for a point through time as a graph.
- Want to be able to handle Geopolygon, Geomultipolygons and shapefiles (from which we extract polygons) - can currently handle polygons.

- Some considerations when working with the raster data:
 - Statistics to be applied to the polygon (mean, std etc.)
 - Handling of partial pixels - what happens when a polygon straddles an edge or is partially outside of one (exclude? include? more than 50%? less than 50%?)
 - the kind of band math we can do (functions) e.g. fractional cover - bare, dry, veg; total cover, optionally combine with rainfall...

- Next tasks:
 - Deploying in EASI
 - Connect input requests and output results to Terria
 - Test


## Flask Dev Server

To run the WPS on localhost modify `pywps.cfg` to point `url` and `outputurl` to `localhost`. `workdir` and `outputpath` should be left as `tmp` and `outputs` respectively for a local dev server and `base_route` should be `/` see example:
```
url=http://localhost:5000
workdir=tmp
outputurl=http://localhost:5000/outputs/
outputpath=outputs
base_route=/
```

Once configured a local server can be run by exporting the `FLASK_APP` environment variable and running flask:

```bash
export FLASK_APP=wps.py
flask run
```

## Gunicorn
Assumes only a single instance of datacube-wps will be started. Multiple instances of datacube-wps will require a shared outputs folder between all instances.

* Define the service URL (e.g https://wps.services.dea.ga.gov.au)
* Modify `pywps.cfg`, in the example case:
```
url=https://wps.services.dea.ga.gov.au
outputurl=https://wps.services.dea.ga.gov.au/outputs/
```
* The wps can be started using gunicorn: `gunicorn -b 0.0.0.0:8000 wps:app`

## Changing Processes in WPS
The processes which are available to users of the WPS are enumerated in the `DEA_WPS_config.yaml` file.

### Resource allocation
The environment variable `DATACUBE_WPS_NUM_WORKERS` sets the number of workers (defaults to 4).

# WPS development testing from Web
## Workflow testing - from terria to wps service
1. Generate a specific terria catalog for wps terria testing http://terria-catalog-tool.dev.dea.ga.gov.au/wps
   - Enter the wps service url or leave default
   - Click Create Catalog button
   - verify the services listed in `json` format is correct
   - change file name if required or leave default
   - Click download catalog button to get a copy of the generated catalog
2. Go to http://terria-cube.terria.io/#clean, Add data
3. Select tab my data
4. Add local data and select the downloaded file

## Individual service debugging testing
### Collect payload
This part is flow-on from Workflow testing
1. Open DevToolsUI and go to `network` tab
2. Under `Data Catalogue` add the wps service needed for testing
3. Complete the Terria form and click Run Analysis button
4. The network will start to run
5. Click on Name = `?service=WPS&request=Execute` and open `Headers` tab
6. The following are used for testing with API tool
   - `xml` under Request Payload
   - `Request URL` under General
### Testing with web API tool
1. Go to http://www.apirequest.io/
2. URL = `request URL` from Collect payload point 6
3. Request body = `xml` from Collect payload point 6

## API
### GetCapabilities
- Returns configured operations and processes in XML format.
- Currently, operations include **GetCapabilities**, **DescribeProcess** and **Execute**. Processes include **Fractional Cover Drill**, **Mangrove Cover Drill** and **WIT polygon drill**
- Locally accessed via http://localhost:8000/?service=WPS&request=GetCapabilities&version=1.0.0

### DescribeProcess
- Returns a description of a configured process in XML format (accepted input formats, data types etc.)
- Returned XML provides framework for input data to execute described process.
- Locally accessed via http://localhost:8000/?service=WPS&version=1.0.0&request=DescribeProcess&identifier=PROCESS-IDENTIFIER

### Execute
- Runs a specified process.
- Inputs depend on process configuration.
- Request can be made as either a GET URL or a POST with an XML request document.
- Sendings requests with XML request documents are preferred for tidiness.
- POSTs can be constructed with assistance from Postman standalone app, Postman Chrome browser extension, Firefox Developer Tools or equivalent tools.
- Example of a CURL call:

curl -H "Content-Type: text/xml" -d @wpsrequest.xml -X POST localhost:8000?service=WPS&request=Execute

- Example of a request XML for the implemented mangrove drill process.

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

- See `./example_request.xml` for another example (process not implemented)

### Terria-WPS communications
In addition to directly sending requests to easi-wps via CURL commands, it can also be interfaced via Terria. With some minimal changes to TerriaMap configuration (https://docs-v8.terria.io/guide/getting-started/), namely, pointing Terria at easi-wps's GetCapabilities URL, inputs and outputs can be directly explored on a map. 

WPS to Terria communications is powered by the DescribeProcess request - upon selection of a process to be run, user input options will be rendered in Terria, according to input datatypes returned via a background DescribeProcess call.

The execution of a process is done via an Execute request, with an input XML generated by Terria. Upon completion of the request, Terria will return an XML stating that the process has finished running as well as the process outputs:

- Pixel drill example:

```xml
<wps:ExecuteResponse xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_response.xsd" service="WPS"
    version="1.0.0" xml:lang="en-US" serviceInstance="http://localhost:8000?request=GetCapabilities&amp;service=WPS"
    statusLocation="http://localhost:8000/outputs/8991789c-b305-11ed-9c3a-0242ac120003.xml">
    <wps:Process wps:processVersion="0.4">
        <ows:Identifier>WOfSDrill</ows:Identifier>
        <ows:Title>Water Observations from Space Pixel Drill</ows:Title>
        <ows:Abstract>
            Water Observations from Space Pixel Drill Water Observations from Space (WOfS) provides surface water
            observations derived from satellite imagery for all of Australia. The current product (Version 2.1.5)
            includes observations taken from 1986 to the present, from the Landsat 5, 7 and 8 satellites. WOfS covers
            all of mainland Australia and Tasmania but excludes off-shore Territories. The WOfS product allows users to
            get a better understanding of where water is normally present in a landscape, where water is seldom
            observed, and where inundation has occurred occasionally. This Pixel Drill will output the water
            observations for a point through time as graph. For service status information, see
            https://status.dea.ga.gov.au.
        </ows:Abstract>
    </wps:Process>
    <wps:Status creationTime="2023-02-22T23:06:41Z">
        <wps:ProcessSucceeded>
            PyWPS Process Water Observations from Space Pixel Drill finished
        </wps:ProcessSucceeded>
    </wps:Status>
    <wps:ProcessOutputs>
        <wps:Output>
            <ows:Identifier>image</ows:Identifier>
            <ows:Title>WOfS Pixel Drill Preview</ows:Title>
            <ows:Abstract />
            <wps:Data>
                <wps:LiteralData dataType="string">None</wps:LiteralData>
            </wps:Data>
        </wps:Output>
        <wps:Output>
            <ows:Identifier>url</ows:Identifier>
            <ows:Title>WOfS Pixel Drill Graph</ows:Title>
            <ows:Abstract />
            <wps:Data>
                <wps:LiteralData dataType="string">None</wps:LiteralData>
            </wps:Data>
        </wps:Output>
        <wps:Output>
            <ows:Identifier>timeseries</ows:Identifier>
            <ows:Title>Timeseries Drill</ows:Title>
            <ows:Abstract />
            <wps:Data>
                <wps:ComplexData mimeType="application/vnd.terriajs.catalog-member+json" encoding="utf-8"
                    schema="https://tools.ietf.org/html/rfc7159">
                    {"data": "time,Observation\n2019-01-06,not observable\n2019-01-14,dry\n2019-01-22,not
                    observable\n2019-01-30,dry\n2019-02-07,not
                    observable\n2019-02-15,dry\n2019-02-23,dry\n2019-03-03,not
                    observable\n2019-03-11,dry\n2019-03-19,dry\n2019-03-27,not
                    observable\n2019-04-04,dry\n2019-04-12,dry\n2019-04-20,dry\n2019-04-28,not
                    observable\n2019-05-06,dry\n2019-05-14,dry\n2019-05-22,not
                    observable\n2019-05-30,dry\n2019-06-07,not observable\n2019-06-15,not
                    observable\n2019-06-23,dry\n2019-07-01,dry\n2019-07-09,not
                    observable\n2019-07-17,dry\n2019-07-25,not
                    observable\n2019-08-02,dry\n2019-08-10,dry\n2019-08-18,dry\n2019-09-03,dry\n2019-09-11,dry\n2019-09-19,dry\n2019-09-27,dry\n2019-10-05,not
                    observable\n2019-10-21,not observable\n2019-10-29,not
                    observable\n2019-11-06,dry\n2019-11-14,dry\n2019-11-22,dry\n2019-11-30,dry\n2019-12-08,not
                    observable\n2019-12-16,not observable\n2019-12-24,not observable\n", "isEnabled": false, "type":
                    "csv", "name": "WOfS", "tableStyle": {"columns": {"Wet": {"units": "#", "chartLineColor": "#4F81BD",
                    "active": true}, "Dry": {"units": "#", "chartLineColor": "#D99694", "active": true}, "Not
                    Observable": {"units": "#", "chartLineColor": "#707070", "active": true}}}}
                </wps:ComplexData>
            </wps:Data>
        </wps:Output>
    </wps:ProcessOutputs>
</wps:ExecuteResponse>
```

- Timeseries example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US" serviceInstance="http://localhost:5000?request=GetCapabilities&amp;amp;service=WPS" statusLocation="http://localhost:5000/outputs/91c8c62a-b2f9-11ed-b842-0242ac120003.xml">
    <wps:Process wps:processVersion="0.2">
        <ows:Identifier>Mangrove Cover Drill</ows:Identifier>
        <ows:Title>Mangrove Cover</ows:Title>
        <ows:Abstract>Performs Mangrove Polygon Drill</ows:Abstract>
        </wps:Process>
    <wps:Status creationTime="2023-02-22T21:40:49Z">
        <wps:ProcessSucceeded>PyWPS Process Mangrove Cover finished</wps:ProcessSucceeded>
        </wps:Status>
        <wps:ProcessOutputs>
                <wps:Output>
            <ows:Identifier>timeseries</ows:Identifier>
            <ows:Title>Timeseries Drill</ows:Title>
            <ows:Abstract></ows:Abstract>
                        <wps:Data>
                    <wps:ComplexData mimeType="application/vnd.terriajs.catalog-member+json" encoding="utf-8" schema="https://tools.ietf.org/html/rfc7159"><![CDATA[{"data": "time,Woodland,Open Forest,Closed Forest\n2019-07-02,0,0,0\n", "isEnabled": true, "type": "csv", "name": "Mangrove Cover", "tableStyle": {"columns": {"Woodland": {"units": "#", "chartLineColor": "#9FFF4C", "active": true}, "Open Forest": {"units": "#", "chartLineColor": "#5ECC00", "active": true}, "Closed Forest": {"units": "#", "chartLineColor": "#3B7F00", "active": true}}}}]]></wps:ComplexData>
                        </wps:Data>
                </wps:Output>
        </wps:ProcessOutputs>
</wps:ExecuteResponse>
```

WPS can serve outputs back to Terria in a variety of formats: 
	- Static timeseries images 
	- Dynamic timeseries with adjustable date ranges
	- Table data rendered in browser.
  - A link to a downloadable CSV

The output format depends on the Execute XML generated by Terria when sending request. When doing so via a CURL request with a custom XML file, the output format can be specified within a ProcessOutputs tag:

```xml
<ProcessOutputs>
    <Output>
        <ows:Identifier>download_link</ows:Identifier>
        <ows:Title>CSV Download Link</ows:Title>
        <ows:Abstract/>
        <LiteralOutput>
            <ows:DataType ows:reference="http://www.w3.org/TR/xmlschema-2/#string">string</ows:DataType>
        </LiteralOutput>
    </Output>
    <Output>
        <ows:Identifier>csv</ows:Identifier>
        <ows:Title>CSV Results</ows:Title>
        <ows:Abstract/>
        <ComplexOutput>
            <Default>
                <Format>
                    <MimeType>application/vnd.terriajs.catalog-member+json</MimeType>
                    <Schema>https://tools.ietf.org/html/rfc7159</Schema>
                </Format>
            </Default>
            <Supported>
                <Format>
                    <MimeType>application/vnd.terriajs.catalog-member+json</MimeType>
                    <Schema>https://tools.ietf.org/html/rfc7159</Schema>
                </Format>
                <Format>
                    <MimeType>text/csv</MimeType>
                    <Schema/>
                </Format>
            </Supported>
        </ComplexOutput>
    </Output>
</ProcessOutputs>
```

Or a ResponseForm tag:

```xml
<wps:ResponseForm>
    <wps:RawDataOutput mimeType="application/vnd.terriajs.catalog-member+json">
      <ows:Identifier>timeseries</ows:Identifier>
    </wps:RawDataOutput>
  </wps:ResponseForm>
```



It is not certain how Terria achieves this as the XML sent as part of an Execute request cannot be directly manipulated - could maybe be configured in the datacube-wps-config.yaml file, as the DescribeProcess request which fetches a process' inputs refers to this config file (Ashley to clear up). It is also currently unclear how Terria renders the XML file returned upon completion of an Execute process
