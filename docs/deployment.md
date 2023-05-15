# Deploy WPS

This is how EASI currently deploys WPS.

1. Build image from datacube-wps repo
1. Deploy using opendatacube/datacube-wps chart, and a deployment-specific flux manifest.
1. Test that service is working

## Development and testing options

These options help bypass the Kubernetes network and load balancers, which may limit or alter the traffic to/from the WPS service.

### JupyterLab

TBA

### Port forward

TBA
