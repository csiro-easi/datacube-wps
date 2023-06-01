# Adding WPS functions

There are three main steps for adding a new WPS function or process:

 - [Add the process to the WPS configuration](#wps-configuration)
 - [Add processing code to undertake the function](#process-handling)
 - Optionally, [Add a Terria catalog item](#terria)

# WPS configuration
To add a new function, you must first create a new configuration for it in `datacube-wps-config.yaml`.

This file is read into WPS Process objects via [ODC virtual product definitions](https://opendatacube.readthedocs.io/en/stable/data-access-analysis/advanced-topics/virtual-products.html).

Notes:

- The product and measurement specified in the input section must be valid (indexed in) your ODC database. The ODC database environment is configured by the standard ODC means (environment specific).
- Other optional keys can be used. Refer to existing config in `datacube-wps-config.yaml` and the virtual products documentation. Custom keys can also be inserted to be used in your function.

As a minimum, the following keys and structure are required:
```
  - process: str

    about:
        identifier: str
        version: str
        title: str
        abstract: str
        store_supported: bool
        status_supported: bool
        geometry_type: "point" | "polygon"

    input:
       product: str
       measurements: [str]

    style:
       csv: bool
       table:
         False |
            columns:
                str:
                    units: str
                    active: bool
```


# Process handling
The next step is to decide whether or not to leverage the base `PixelDrill` or `PolygonDrill` classes defined in `datacube_wps/processes/__init__.py`. Or a custom base classes could be added to handle inputs, queries and render outputs differently. For most general applications, the base classes are sufficient to handle your function. Note that you will have to write new tests if creating a custom class.

*Python code
Now that your query/request handling and inputs and outputs are defined, the next step is to write the code for your function. This file should sit in `processes/`. There are many ways to do this but in general, you want to create a class with functions to:
 - process data
 - render outputs

and optionally:
 - mask data
 - render Altair chart

 If you have chosen to use the base classes for process handling, the existing functions in ../processes can be used as a general guideline.

 # Terria
 To integrate this function with Terria, you will need to add a dictionary to /terria/TerriaMap/wwwroot/init/simple.json. As a minimum, the following keys are required:

```json
 {
    {
      "id": "name of function",
      "type": "wps",
      "storeSupported": true,
      "statusSupported": true,
      "url": "mywps/?service=WPS",
      "identifier": "name of function",
      "forceConvertResultsToV8": true
    },
    "corsDomains": [
        "mywps"
    ]
 }
```

 The identifier value must match the identifier specified in ../datacube-wps-config.yaml. Also note that your WPS address must be included in the allowed CORS domains for communication to work. 
 
 For more Terria configuration options for your function, see: https://docs.terria.io/guide/connecting-to-data/catalog-type-details/wps/

 For more customisation options for the look and feel of your Terria setup (starting map position, camera position, zoom levels etc.), see: https://docs.terria.io/guide/customizing/initialization-files/
