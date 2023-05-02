# Specifying configuration
To add a new function, you must first create a new configuration for it in ../datacube-wps-config.yaml. As a minimum, the following keys and structure are required:
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

The product and measurement specified in the input section must be valid i.e. indexed into your database. If using the default Postgres database, this can be done through the query ran by ../setup-db.sh.

Other optional keys can be used - refer to existing config in ../datacube-wps-config.yaml. Custom keys can also be inserted to be used in your function.

# Process handling
The next step is to decide whether or not to leverage the base PixelDrill or PolygonDrill classes defined in ../datacube_wps/processes/__init__.py, or to create a custom class to handle inputs,queries, render outputs etc. differently. For most general applications, the base classes are sufficient to handle your function. Note that you will have to write new tests if creating a custom class.

*Python code
Now that your query/request handling and inputs and outputs are defined, the final step is to write the code for your function! This file should sit in ../processes. There are many ways to do this but in general, you want to create a class with functions to:
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
