# Code overview for developers

- Main elements
- Workflow through the code
- Set limits
- Use dask

## Main elements

| Item | description
|--|--|
| `pywps.cfg` | PyWPS configuration |
| `setup-db.sh` | [dev] Create an index data into an ODC database |
| `gunicorn.conf.py` | Gunicorn configuration |
| `datacube-wps-config.yaml` | Define the WPS processes |
| `outputs/` | Output directory for storing results (and WIP) |
| `logs/` | PyWPS sqlite logs |
| `docs/` | Developer and user documentation |
| `datacube_wps/__init__.py` | Start the flask app |
| `datacube_wps/impl.py` | Define the flask app, routes etc |
| `datacube_wps/processes/__init__.py` | Generic PixelDrill and PolygonDrill implementations |
| `datacube_wps/processes/*.py` | Specific Process implementations |

PyWPS handles the incoming traffic and communications with the requester.

Process are defined in `datacube-wps-config.yaml` and implemented in `datacube_wps/processes/*`.

## Define Processes

The Processes in `datacube-wps` use [ODC Virtual Products (VPs)](https://datacube-core.readthedocs.io/en/latest/data-access-analysis/advanced-topics/virtual-products.html). The type of VP is given in `datacube-wps-config.yaml`.

Start up:

- Read `datacube-wps-config.yaml`
- Create VP type
- Create PyWPS Process

## Request workflow

## Set limits

## Use dask
