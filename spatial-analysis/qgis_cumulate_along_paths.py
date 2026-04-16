from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterString,
    QgsProcessing,
    QgsProject,
)
from qgis import processing


class CumulateAlongPathsAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYER = "INPUT_LAYER"
    OUTPUT_LAYER = "OUTPUT_LAYER"
    DEBUG = False
    DISSOLVE_FIELD = "DISSOLVE_FIELD"  # i.e.subrides

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER, "Wege als Linien-Layer", [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DISSOLVE_FIELD,
                "Dissolve Feld-Name",
                defaultValue="subrides",
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        sp_layer = self.parameterAsLayer(parameters, self.INPUT_LAYER, context)
        dissolve_field = self.parameterAsString(parameters, self.DISSOLVE_FIELD, context)

        feedback.pushInfo("Dissolving paths…")
        dissolve_result = processing.run(
            "native:dissolve",
            {
                "INPUT": sp_layer,
                "FIELD": [],
                "SEPARATE_DISJOINT": False,
                "OUTPUT": "memory:dissolve",
            },
            context=context,
            feedback=feedback,
        )
        dissolved_layer = dissolve_result["OUTPUT"]
        if self.DEBUG:
            QgsProject.instance().addMapLayer(dissolved_layer)

        feedback.pushInfo("Exploding lines…")
        explode_result = processing.run(
            "native:explodelines",
            {"INPUT": dissolved_layer, "OUTPUT": "memory:exploded_sp"},
            context=context,
            feedback=feedback,
        )
        explode_layer = explode_result["OUTPUT"]
        if self.DEBUG:
            QgsProject.instance().addMapLayer(explode_layer)

        feedback.pushInfo("Joining by location…")
        join_result = processing.run(
            "native:joinbylocationsummary",
            {
                "INPUT": explode_layer,
                "PREDICATE": [0],
                "JOIN": sp_layer,
                "JOIN_FIELDS": [],
                "SUMMARIES": [],
                "DISCARD_NONMATCHING": False,
                "OUTPUT": "memory:cum_shorest_path",
            },
            context=context,
            feedback=feedback,
        )
        joined_layer = join_result["OUTPUT"]

        if isinstance(dissolve_field, str) and len(dissolve_field.strip()) > 0:
            dissolve_path_result = processing.run(
                "native:dissolve",
                {
                    "INPUT": joined_layer,
                    "FIELD": [dissolve_field + "_sum"],
                    "SEPARATE_DISJOINT": False,
                    "OUTPUT": "memory:dissolved_path",
                },
                context=context,
                feedback=feedback,
            )
            output_layer = dissolve_path_result["OUTPUT"]
        else:
            output_layer = joined_layer

        update_fid(output_layer)
        QgsProject.instance().addMapLayer(output_layer)

        return {self.OUTPUT_LAYER: output_layer}

    def shortHelpString(self):
        return (
            "Aufsummieren der Attribute überlagernder Wege\n"
            "\n 1) Die Wege im Eingabelayer werden in einzelne Linien-Segmente zerlegt, die jeweils nur aus 2 Punkten bestehen."
            "\n 2) Für jedes Segment werden die Attribute aller überlagernder Wege statisitsch ausgewertet. Details zu den Statistiken sind in QGIS unter joinByLocation(summary) zu finden."
            "\n\nHinweis zum dissolve-Feld:"
            "\nDer Ausgabe-Layer besteht aus sehr vielen Linien-Segmenten mit je 2 Punkten."
            "Diese Segmente können anhand des dissovle-Feldes in längere Segmente mit gleichem Feldwert gruppiert werden, um die Geometrie effizienter zu speichern."
        )

    def name(self):
        return "cumulate_along_path_algorithm"

    def displayName(self):
        return "3 Cumulate over line segments"

    def group(self):
        return "ICLmobil"

    def groupId(self):
        return "mobility"

    def createInstance(self):
        return CumulateAlongPathsAlgorithm()


def update_fid(layer):
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        feature["fid"] = i
        i = i + 1
        layer.updateFeature(feature)

    layer.commitChanges()
