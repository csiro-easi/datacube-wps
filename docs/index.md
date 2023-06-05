# datacube-wps

The datacube-wps package deploys web processing services ([pyWPS](https://pywps.org/)) in an opendatacube environment. This repository was forked from https://github.com/opendatacube/datacube-wps and has been modifed to be used in the CSIRO EASI platforms. Of note, we have added (or will add):

- Code updates to track changes in datacube-core and other opendatacube packages
- Additional WPS processes for EASI products
- Dask capability
- Guardrails to ensure requests are reasonable.

## Index

- [Usage examples](examples.md)
- [Using WPS with TerriaJS](terriajs.md)
- [Code overview for developers](developer.md)
- [Adding new functions](adding_new_functions.md)
- [Test and deploy WPS](deployment.md)
