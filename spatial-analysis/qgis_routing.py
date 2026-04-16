from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsVectorLayer,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessing,
    QgsProject,
)

from qgis import processing


class CustomRoutingAlgorithm(QgsProcessingAlgorithm):
    NETWORK = "NETWORK"
    ORIGINS = "ORIGINS"
    DEST = "DEST"
    OUTPUT = "OUTPUT"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.NETWORK, "Straßennetz als Linien-Layer", [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ORIGINS, "Startpunkte als Punkt-Layer (key=\"fid\")", [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.DEST, "Zielpunkt(e) als Punkt-Layer", [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Kürzeste Wege je Ausgangspunkt (key=\"fid\")")
        )

    def processAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        network_layer = self.parameterAsLayer(parameters, self.NETWORK, context)
        origins_layer = self.parameterAsLayer(parameters, self.ORIGINS, context)
        dest_layer = self.parameterAsLayer(parameters, self.DEST, context)
        dest_feature = next(dest_layer.getFeatures())
        dest = dest_feature.geometry().asPoint()

        sp = routing(feedback, context, network_layer, origins_layer, dest)

        QgsProject.instance().addMapLayer(sp)

        return {self.OUTPUT: sp}

    def shortHelpString(self):
        return (
            "Berechnung der kürzesten Wege von den Startpunkten zum Zielpunkt auf dem Straßennetz.\n\n"
            "Verknüpfung: \"fid\" des Startpunktes ist \"fid\" im Ausgabelayer"
        )


    def name(self):
        return "custom_routing_alorithm"

    def displayName(self):
        return "2a Routing Tool (shortest)"

    def group(self):
        return "ICLmobil"

    def groupId(self):
        return "mobility"

    def createInstance(self):
        return CustomRoutingAlgorithm()


def routing(
    feedback,
    context,
    network_layer: QgsVectorLayer,
    origins_layer: QgsVectorLayer,
    dest_coords: str,
):
    sp_result = processing.run(
        "native:shortestpathlayertopoint",
        {
            "INPUT": network_layer,
            "STRATEGY": 0,
            "DIRECTION_FIELD": "",
            "VALUE_FORWARD": "",
            "VALUE_BACKWARD": "",
            "VALUE_BOTH": "",
            "DEFAULT_DIRECTION": 2,
            "SPEED_FIELD": "",
            "DEFAULT_SPEED": 50,
            "TOLERANCE": 0,
            "START_POINTS": origins_layer,
            "END_POINT": dest_coords,
            "OUTPUT": "memory:shortest_paths",
        },
        context=context,
        feedback=feedback,
    )
    return sp_result["OUTPUT"]


def update_fid(layer):
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        feature["fid"] = i
        i = i + 1
        layer.updateFeature(feature)

    layer.commitChanges()
