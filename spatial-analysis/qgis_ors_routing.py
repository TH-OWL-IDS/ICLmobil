from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessing,
    QgsProject,
)
from qgis import processing

# Api-Key:
# 5b3ce3597851110001cf62486b152884969b4783b8400773bd93a6c2


class CustomOrsRouting(QgsProcessingAlgorithm):
    ORIGINS = "ORIGINS"
    DESTINATIONS = "DESTINATIONS"
    OUTPUT = "OUTPUT"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ORIGINS, "Startpunkte als Punkt-Layer (key= \"fid\")", [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.DESTINATIONS,
                "Zielpunkt(e) als Punkt-Layer",
                [QgsProcessing.TypeVectorPoint],
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        origins = self.parameterAsLayer(parameters, self.ORIGINS, context)
        destinations = self.parameterAsLayer(parameters, self.DESTINATIONS, context)

        feedback.pushInfo(f"#origins={origins.featureCount()}")
        feedback.pushInfo(f"#destinations={destinations.featureCount()}")

        result = processing.run(
            "ORS Tools:directions_from_points_2_layers",
            {
                "INPUT_PROVIDER": 0,
                "INPUT_PROFILE": 0,
                "RADIUSES": [1000, 1000],
                "INPUT_START_LAYER": origins,
                "INPUT_START_FIELD": "fid",
                "INPUT_SORT_START_BY": "",
                "INPUT_END_LAYER": destinations,
                "INPUT_END_FIELD": "name",
                "INPUT_SORT_END_BY": "",
                "INPUT_PREFERENCE": 0,  # fastest
                "INPUT_MODE": 1,
                "EXTRA_INFO": [],
                "CSV_FACTOR": None,
                "CSV_COLUMN": "",
                "INPUT_AVOID_FEATURES": [],
                "INPUT_AVOID_BORDERS": None,
                "INPUT_AVOID_COUNTRIES": "",
                "INPUT_AVOID_POLYGONS": None,
                "OUTPUT": "memory:routes",
            },
            context=context,
            feedback=feedback,
        )
        route_layer = result["OUTPUT"]

        feedback.pushInfo("join routes with point attributes")
        join_attr_result = processing.run(
            "native:joinattributestable",
            {
                "INPUT": route_layer,
                "FIELD": "FROM_ID",
                "INPUT_2": origins,
                "FIELD_2": "fid",
                "FIELDS_TO_COPY": [],
                "METHOD": 1,
                "DISCARD_NONMATCHING": True,
                "PREFIX": "",
                "OUTPUT": "memory:data_shortes_paths",
            },
        )
        route_layer = join_attr_result["OUTPUT"]
        QgsProject.instance().addMapLayer(route_layer)

        return {self.OUTPUT: route_layer}
  
    def shortHelpString(self):
        return (
           "Berechnung der schnellsten Wege von den Ausgangspunkten zum Zielpunkt.\n"
           "Vorraussetzung ist, dass das ORS-Tools plugin installiert ist und ein API-Key gesetzt ist.\n\n"
           "Verknüpfung: \"fid\" des Startpunktes ist \"fid\" im Ausgabelayer"
        )

    def name(self):
        return "ors_routing"

    def displayName(self):
        return "2b Custom ORS-Routing (fastest)"

    def group(self):
        return "ICLmobil"

    def groupId(self):
        return "mobility"

    def createInstance(self):
        return CustomOrsRouting()
