import json
from typing import Callable
from pathlib import Path
from TripApiResponse import Journey
from TripResult import TripResult


def trip_results_to_geojson(trip_results: dict[str, TripResult]) -> dict:

    features = []
    trip_count = 0
    i=0
    total = len(trip_results)
    for trip_index, trip_result in trip_results.items():
        percent = (i / total) * 100
        i+=1 
        print(f"converting trips: {i}/{total} ({percent:.1f}%)", end="\r")

        if (
            isinstance(trip_result.trip, str)
            or trip_result.trip is None
            or trip_result.trip.journeys is None
        ):
            print("invalid trip: " + trip_index)
            continue

        trip_count = trip_count + 1
        for journey_index, journey in enumerate(trip_result.trip.journeys):
            multilines = []

            for leg_index, leg in enumerate(journey.legs):
                if leg.coords:

                    coords = [
                        (
                            [coord[1], coord[0]]
                            if isinstance(coord, list)
                            else [coord.d, coord.z]
                        )
                        for coord in leg.coords
                    ]

                    coords_cleaned = [
                        c for c in coords if c is not None and len(c) >= 2
                    ]

                    # Leg-Feature
                    leg_feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coords_cleaned,
                        },
                        "properties": {
                            "origin_id": leg.origin.id,
                            "destination": leg.destination.name,
                            "destination_id": leg.destination.id,
                            "transportation": (
                                getattr(
                                    getattr(leg, "transportation", None),
                                    "product",
                                    None,
                                )
                                and leg.transportation.product.name
                            ),
                            "distance": leg.distance,
                            "duration": leg.duration,
                            "trip_index": trip_index,
                            "interchanges": journey.interchanges,
                            "journey_duration": journey.getDurationMin(),
                            "journey_index": journey_index,
                            "fid": trip_result.fid,
                            "leg_index": leg_index,
                        },
                    }
                    features.append(leg_feature)

                    multilines.append(coords_cleaned)

    geojson = {"type": "FeatureCollection", "features": features}

   
    geojson["crs"] = {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
    }
    print(f"converted {trip_count}/{len(trip_results)} trips succesfully")
    return geojson


def best_by_duration(journeys: list[Journey]) -> Journey:
    return min(journeys, key=lambda j: j.getDurationMin())


def select_best_journeys(
    trip_results: dict[str, TripResult], predicate: Callable[[list], object]
) -> dict[str, TripResult]:

    filtered_results = {}
    trip_count = 0
    i=0
    total = len(trip_results)
    for trip_index, trip_result in trip_results.items():
       
        percent = (i / total) * 100
        i+=1 
        print(f"converting trips: {i}/{total} ({percent:.1f}%)", end="\r")
       
        if (
            isinstance(trip_result.trip, str)
            or trip_result.trip is None
            or not trip_result.trip.journeys
        ):
            filtered_results[trip_index] = trip_result
            continue

        best_journey = predicate(trip_result.trip.journeys)

        if best_journey:
            trip_result.trip.journeys = [best_journey]
            filtered_results[trip_index] = trip_result

    return filtered_results


def list_json_files(dir_path: Path) -> list[Path]:
    return list(dir_path.glob("*.json"))


def load_trip_results(path: str) -> dict[str, TripResult]:
    directory = Path(path)

    results = {}
    files = list_json_files(directory)
    total_files = len(files)
    for i, f in enumerate(files, start=1):
        percent = (i / total_files) * 100
        print(f"Loading files {i}/{total_files} ({percent:.1f}%)", end="\r")
        results[f.name] = TripResult(**json.loads(f.read_text()))
    print()
    return results



def convertBatch(datapath:str, outputpath:str, ):
    print("### loading trip results ###")
    # tr = load_trip_results("trips_test")
    tr = load_trip_results(datapath)
    
    print("DONE\n\nfilter best journeys")
    # filter shortest journey for each trip
    tr = select_best_journeys(tr, best_by_duration)

    print(f"converting {len(tr)} trip results to geojson")
    geojson_data = trip_results_to_geojson(tr)
    print(f"saving {len(geojson_data.get('features'))} features to geojson")

    with open(outputpath+".geojson", "w") as f:
        json.dump(geojson_data, f)

    print("GeoJSON mit MultiLineStrings exportiert.")

if __name__ == "__main__":
    convertBatch("trips", "geotrips");
