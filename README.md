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
- Terria, if used, will construct execute request from browser.
- Otherwise request can be made as either a GET URL or a POST with an XML request document.
- POSTs can be constructed with assistance from Postman standalone app, Postman Chrome browser extension, Firefox Developer Tools or equivalent tools.
- Example of a CURL call:

curl -H "Content-Type: text/xml" -d @wpsrequest.xml -X POST localhost:8000?service=WPS&request=Execute


### Terria-WPS communications
In addition to directly sending requests to easi-wps via CURL commands, it can also be interfaced via Terria. With some minimal changes to TerriaMap configuration (https://docs-v8.terria.io/guide/getting-started/), namely, pointing Terria at easi-wps's GetCapabilities URL, inputs and outputs can be directly explored on a map. 

WPS to Terria communications is powered by the DescribeProcess request - upon selection of a process to be run, user input options will be rendered in Terria, according to input datatypes returned via a background DescribeProcess call.

The execution of a process is done via an Execute request, with an input XML generated by Terria. Upon completion of the request, Terria will return an XML stating that the process has finished running as well as the process outputs:

WPS can serve outputs back to Terria in a variety of formats: 
	- Static timeseries images 
	- Dynamic timeseries with adjustable date ranges
	- Table data rendered in browser.
    - A link to a downloadable CSV

These need to be configured in ../datacube_wps/processes/__init__.py