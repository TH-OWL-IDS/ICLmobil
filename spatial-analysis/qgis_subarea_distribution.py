from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsVectorLayer,
    QgsField,
    QgsProcessing,
    QgsProject,
)
from collections import defaultdict

from qgis import processing


class DistributeAreaAttributeAlgorithm(QgsProcessingAlgorithm):
    # Parameter-Keys
    PLZ_LAYER = "PLZ_LAYER"
    PLZ_FIELD = "PLZ_FIELD"

    CLC_LAYER = "WGC_LAYER"
    CSV_LAYER = "CSV_LAYER"
    PLZ_FIELD_CSV = "PLZ_FIELD_CSV"
    DATA_FIELD_CSV = "DATA_FIELD_CSV"
    AREA_THRESHOLD = "AREA_THRESHOLD"

    OUTPUT_LAYER = "OUTPUT_LAYER"
    OUTPUT_LAYER2 = "OUTPUT_LAYER2"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PLZ_LAYER, "PLZ-Gebiete als Polygon-Layer", [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CLC_LAYER, "Wohngebiete als Polygon-Layer (CLC)", [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CSV_LAYER, "CSV-Daten als Daten-Layer", [QgsProcessing.TypeFile]
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PLZ_FIELD, "PLZ-Feld im PLZ-Layer", defaultValue="plz_code"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PLZ_FIELD_CSV, "PLZ-Feld im CSV-Layer", defaultValue="PLZ"
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.DATA_FIELD_CSV,
                "Datenfeld im CSV-Layer",
                defaultValue="Lemgo",
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.AREA_THRESHOLD,
                "[Optional] Flächenschwellenwert (m²) zur Unterdrückung kleiner Gebiete",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=500000,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        plz_layer = self.parameterAsLayer(parameters, self.PLZ_LAYER, context)
        wgc_layer = self.parameterAsLayer(parameters, self.CLC_LAYER, context)
        csv_layer = self.parameterAsLayer(parameters, self.CSV_LAYER, context)

        plz_field = self.parameterAsString(parameters, self.PLZ_FIELD, context)
        plz_field_csv = self.parameterAsString(parameters, self.PLZ_FIELD_CSV, context)
        data_field_csv = self.parameterAsString(
            parameters, self.DATA_FIELD_CSV, context
        )

        area_threshold = self.parameterAsString(
            parameters, self.AREA_THRESHOLD, context
        )

        feedback.pushInfo(f"#plz={plz_layer.featureCount()}")
        feedback.pushInfo(f"#csv={csv_layer.featureCount()}")
        feedback.pushInfo(f"#clc={wgc_layer.featureCount()}")

        area_field = "area_m2"

        # 1 compute intersecion
        wgc_clip_layer = intersection(feedback, context, plz_layer, wgc_layer)
        feedback.pushInfo(f"#clc_clip={wgc_clip_layer.featureCount()}")

        # 2 compute area of subareas
        feedback.pushInfo("compute area of clipped clc...")
        compute_area(wgc_clip_layer, area_field)
        threshold_area(wgc_clip_layer, area_field, plz_field, area_threshold)
        feedback.pushInfo(
            f"#clc_clip:area thresholded = {wgc_clip_layer.featureCount()}"
        )

        # compute sum of wgc area per plz
        sum_area = defaultdict(float)
        for feature in wgc_clip_layer.getFeatures():
            plz = feature[plz_field]
            area = feature["area_m2"]
            # area = feature.geometry().area()
            sum_area[plz] += area

        # get rides by plz
        rides_plz = defaultdict(float)
        for feature in csv_layer.getFeatures():
            plz = str(feature[plz_field_csv])
            rides = feature[data_field_csv]
            rides_plz[plz] = rides
            # print(f"Plz: {plz}, #={rides}")

        wgc_clip_layer.startEditing()

        field_names = [field.name() for field in wgc_clip_layer.fields()]
        if "rides_plz" not in field_names:
            wgc_clip_layer.dataProvider().addAttributes(
                [QgsField("rides_plz", QVariant.Double)]
            )
            wgc_clip_layer.updateFields()

        if "subrides" not in field_names:
            wgc_clip_layer.dataProvider().addAttributes(
                [QgsField("subrides", QVariant.Double)]
            )
            wgc_clip_layer.updateFields()

        if "wgc_area_plz_total" not in field_names:
            wgc_clip_layer.dataProvider().addAttributes(
                [QgsField("wgc_area_plz_total", QVariant.Double)]
            )
            wgc_clip_layer.updateFields()

        if "wgc_area_plz_rel" not in field_names:
            wgc_clip_layer.dataProvider().addAttributes(
                [QgsField("wgc_area_plz_rel", QVariant.Double)]
            )
            wgc_clip_layer.updateFields()

        for feature in wgc_clip_layer.getFeatures():
            plz = feature[plz_field]
            area = feature["area_m2"]
            plz_area = sum_area[plz]
            rides = rides_plz[plz]
            feature["wgc_area_plz_total"] = plz_area
            feature["wgc_area_plz_rel"] = area / plz_area
            feature["rides_plz"] = rides
            feature["subrides"] = float(rides) * area / plz_area
            wgc_clip_layer.updateFeature(feature)

        wgc_clip_layer.commitChanges()

        wgc_clip_layer.startEditing()

        for feature in wgc_clip_layer.getFeatures():
            if feature["rides_plz"] == 0:
                wgc_clip_layer.deleteFeature(feature.id())

        wgc_clip_layer.commitChanges()

        # check if all plz with rides > 0 are in wgc layer
        set_plz_wgc, wgc_total = getPlzRides(wgc_clip_layer, plz_field, "rides_plz")
        set_plz_csv, csv_total = getPlzRides(csv_layer, plz_field_csv, data_field_csv)
        if wgc_total != csv_total:
            missing_plz = set_plz_csv.difference(set_plz_wgc)
            if len(missing_plz) > 0:
                feedback.pushInfo(f"\n⚠️ Fehlende Attribute: {len(missing_plz)}")
                feedback.pushInfo(
                    f"📊 Summenvergleich — CSV: {csv_total}, CLC: {wgc_total} ({(wgc_total/csv_total):.2%})"
                )
                missing_plz_list = ", ".join(sorted(map(str, missing_plz)))
                feedback.pushInfo(f"🔍 Fehlende Attribute: {missing_plz_list}")

        # 3 wgs centroids to match with plz
        wgc_centroids_layer = compute_centroids(feedback, context, wgc_clip_layer)
        feedback.pushInfo("\nDone")

        QgsProject.instance().addMapLayer(wgc_clip_layer)
        QgsProject.instance().addMapLayer(wgc_centroids_layer)

        return {
            self.OUTPUT_LAYER: wgc_centroids_layer,
            self.OUTPUT_LAYER2: wgc_clip_layer,
        }

    def shortHelpString(self):
        return (
           "Verteilung der Fahrten auf Wohngebiete:\n"
            "\nZiel ist es, die Anzahl der Fahrten je PLZ-Gebiet auf ausgewiesene Wohngebiete zu verteilen, um eine realistischere Verteilung zu approximieren. "
            "\nAblauf:"
            "\n1)	Für jedes PLZ-Gebiet wird die Summe der Flächen aller Wohngebiete berechnet."
            "\n2)	Optional: Flächen-Threshold auf Wohngebiete anwenden, um winzige \"subrides\" zu vermeiden."
            "\n               (Für jede PLZ verbleibt stets min. ein Wohngebiet unabhängig von der Fläche) "
            "\n3)	Für jedes Wohngebiet wird der relative Flächenanteil berechnenet. ERZEUGT KEYS = \"fid\""
            "\n4)	Verteilung der Fahrten je PLZ aus CSV-Layer auf die Wohngebiete gemäß ihres Flächenanteils."
            "\nAusgabe:"
            "\nWohngebiete(\"fid\") als Polygon- und Punkt-Layer mit folgenden neuen Feldern:"
            +"\n\"area_m2\": Fläche des Wohngebietes in m²"
            +"\n\"wgc_area_plz_total\": Gesamtfläche aller Wohngebiete im PLZ-Gebiet in m²"
            +"\n\"wgc_area_plz_rel\": Flächenanteil des Wohngebietes im PLZ-Gebiet"
            +"\n\"rides_plz\": Anzahl Fahrten im PLZ-Gebiet"
            +"\n\"subrides\": Anteilige Fahrten des Wohngebiets nach Fläche"
        )

    def name(self):
        return "distribute_area_attribute_algorithm"

    def displayName(self):
        return "1 Area Attribute Distribution"

    def group(self):
        return "ICLmobil"

    def groupId(self):
        return "mobility"

    def createInstance(self):
        return DistributeAreaAttributeAlgorithm()


def update_fid(layer):
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        feature["fid"] = i
        i = i + 1
        layer.updateFeature(feature)

    layer.commitChanges()


def compute_area(layer, area_field_name):
    layer.startEditing()

    field_names = [field.name() for field in layer.fields()]
    if area_field_name not in field_names:
        layer.dataProvider().addAttributes([QgsField(area_field_name, QVariant.Double)])
        layer.updateFields()
    for feature in layer.getFeatures():
        geom = feature.geometry()
        area = geom.area()
        feature[area_field_name] = area
        layer.updateFeature(feature)

    layer.commitChanges()


def intersection(feedback, context, plz_layer, wgc_layer):

    intersection_result = processing.run(
        "native:intersection",
        {
            "INPUT": wgc_layer,
            "OVERLAY": plz_layer,
            "INPUT_FIELDS": [],
            "OVERLAY_FIELDS": [],
            "OVERLAY_FIELDS_PREFIX": "",
            "OUTPUT": "memory:clc_childs",
            "GRID_SIZE": None,
        },
        context=context,
        feedback=feedback,
    )
    layer = intersection_result["OUTPUT"]
    update_fid(layer)
    return layer


def threshold_area(
    layer: QgsVectorLayer, area_field: str, plz_field: str, threshold: int
):

    area_threshold = int(threshold)
    count = 0

    # 1. PLZ Feature-IDs map
    plz_feats = {}
    for feat in layer.getFeatures():
        plz = feat[plz_field]
        if plz not in plz_feats:
            plz_feats[plz] = []
        plz_feats[plz].append((feat.id(), feat[area_field]))

    # 2. collect ids to delete
    ids_to_delete = []

    for plz, feats in plz_feats.items():
        # get feat below threhold
        small_feats = [fid for fid, area in feats if area <= area_threshold]

        # only delete if at least one feat left
        if len(feats) - len(small_feats) >= 1:
            ids_to_delete.extend(small_feats)
        else:
            # if all small, keep the largest
            if len(feats) > 1:
                feats_sorted = sorted(feats, key=lambda x: x[1])  # sortiere nach Fläche
                ids_to_delete.extend(
                    [fid for fid, area in feats_sorted[:-1]]
                )  
    # 3. edit layer
    layer.startEditing()

    layer.deleteFeatures(ids_to_delete)
    count = len(ids_to_delete)

    print(f"area threshold: removed {count} features")
    layer.commitChanges()



def compute_centroids(feedback, context, layer):
    print("\n3 compute wgc centroids")
    centroid_result = processing.run(
        "native:centroids",
        {
            "INPUT": layer,
            "ALL_PARTS": False,
            "OUTPUT": "memory:clc_child_centroids",
        },
        context=context,
        feedback=feedback,
    )
    # note: copies area_m2 already to point layer
    return centroid_result["OUTPUT"]


def getPlzRides(layer, plz_field: str, rides_field: str):
    plz_set = set()
    plz_rides = {}
    total_rides = 0
    print(f"featureCount {layer.name()} = {layer.featureCount()}")
    for feat in layer.getFeatures():
        plz = feat[plz_field]
        rides = float(feat[rides_field])
        if plz is None:
            print(f"\tmissing field in feat id: {feat.id()}")
        else:
            plz_rides[plz] = rides
            if rides > 0:
                plz_set.add(str(plz))

    for k, v in plz_rides.items():
        total_rides += v

    print(f"Total rides: {total_rides}")
    return plz_set, total_rides
