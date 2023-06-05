# Test and deploy WPS

This is how EASI currently deploys WPS.

1. Build image from datacube-wps repo (see "easi-workflows-images" repo)
1. Deploy using opendatacube/datacube-wps chart, and a deployment-specific flux manifest.
1. Restart the flux deployment to pic up the new image
1. Test that the WPS server is working

## Development and testing options

These options help bypass the Kubernetes network and load balancers, which may limit or alter the traffic to/from the WPS server.

### JupyterLab

```bash
cd ~/datacube-wps

# Create a virtual environment
MYENV=wps
python -m venv ~/venvs/$MYENV
source ~/venvs/$MYENV/bin/activate

# Install requirements
pip install flask    # Do this before linking to system site-packages
realpath /env/lib/python3.10/site-packages > ~/venvs/$MYENV/lib/python3.10/site-packages/base_venv.pth
pip install -r requirements.txt   # in datacube-wps
mkdir logs outputs
```

Edit pywps.cfg (not sure if all these are critical)
```
url=https://localhost:5000
outputurl=https://localhost:5000/outputs/
outputpath=/home/jovyan/datacube-wps/outputs
base_route=/home/jovyan/datacube-wps
```

Run flask
```bash
flask --app datacube_wps:app run
```

WPS should be available (replace USERNAME with your username):

https://hub.dev.easi-eo.solutions/user/USERNAME/proxy/5000?service=WPS&version=1.0.0&request=GetCapabilities

### Port forward

TBA
