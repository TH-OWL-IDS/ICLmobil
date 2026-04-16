from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo
from StopApiResponse import StopResponse
from TripApiResponse import TripResponse
from TripResult import TripResult
from GeoConverterML import convertBatch
from PtGeoJson import *
import shutil, time, requests, json

# BASE_URL = "https://openservice-test.vrr.de/openservice/"
BASE_URL = "https://www.vrr.de/vrr-efa/"

FIXED_PARAMS = {
    "allInterchangesAsLegs": "1",
    "changeSpeed": "normal",
    "coordOutputDistance": "1",
    "coordOutputFormat": "WGS84[dd.ddddd]",
    "genC": "1",
    "genMaps": "0",
    "imparedOptionsActive": "1",
    "inclMOT_0": "true",
    "inclMOT_1": "true",
    "inclMOT_10": "true",
    "inclMOT_11": "true",
    "inclMOT_12": "true",
    "inclMOT_13": "true",
    "inclMOT_17": "true",
    "inclMOT_18": "true",
    "inclMOT_19": "true",
    "inclMOT_2": "true",
    "inclMOT_3": "true",
    "inclMOT_4": "true",
    "inclMOT_5": "true",
    "inclMOT_6": "true",
    "inclMOT_7": "true",
    "inclMOT_8": "true",
    "inclMOT_9": "true",
    "includedMeans": "checkbox",
    "itOptionsActive": "1",
    "itdDateDayMonthYear": "06.05.2025",
    "itdTime": "08:00",
    "itdTripDateTimeDepArr": "arr",  # time refers to arrival time!
    "language": "de",
    "lineRestriction": "400",
    "locationServerActive": "1",
    "maxChanges": "9",
    "name_destination": "de:05766:20094",
    "name_origin": "de:05774:7268",
    "outputFormat": "rapidJSON",
    "ptOptionsActive": "1",
    "routeType": "LEASTTIME",
    "serverInfo": "1",
    "sl3plusTripMacro": "1",
    "trITMOTvalue100": "10",
    "type_destination": "any",
    "type_notVia": "any",
    "type_origin": "any",
    "type_via": "any",
    "useElevationData": "1",
    "useProxFootSearch": "true",
    "useRealtime": "1",
    "useUT": "1",
    "version": "10.6.14.22",
    "vrrTripMacro": "1",
}


def fetch_stops(coord_name) -> StopResponse:
    base_url = BASE_URL + "/XML_STOPFINDER_REQUEST"
    params = {"type_sf": "coord", "name_sf": coord_name, "outputFormat": "rapidJSON"}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = json.loads(response.content)
        return StopResponse(**data)
    else:
        print(f"Fehler beim Abrufen der Daten für {coord_name}: {response.status_code}")
        return None


def fetch_trips(
    date: str, time: str, origin: str, destination: str, save: bool = False
) -> TripResponse:
    # set default parameter
    params = FIXED_PARAMS.copy()

    # set trip parameter
    params.update(
        {
            "itdDateDayMonthYear": date,
            "itdTime": time,
            "name_origin": origin,
            "name_destination": destination,
        }
    )
    response = requests.get(BASE_URL + "XML_TRIP_REQUEST2", params=params)
    # print(response.request.url)
    # url = "https://www.vrr.de/vrr-efa/XML_TRIP_REQUEST2?allInterchangesAsLegs=1&changeSpeed=normal&coordOutputDistance=1&coordOutputFormat=WGS84[dd.ddddd]&genC=1&genMaps=0&imparedOptionsActive=1&inclMOT_0=true&inclMOT_1=true&inclMOT_10=true&inclMOT_11=true&inclMOT_12=true&inclMOT_13=true&inclMOT_17=true&inclMOT_18=true&inclMOT_19=true&inclMOT_2=true&inclMOT_3=true&inclMOT_4=true&inclMOT_5=true&inclMOT_6=true&inclMOT_7=true&inclMOT_8=true&inclMOT_9=true&includedMeans=checkbox&itOptionsActive=1&itdDateDayMonthYear=06.05.2025&itdTime=08:00&itdTripDateTimeDepArr=arr&language=de&lineRestriction=400&locationServerActive=1&maxChanges=9&name_destination=de:05766:20094&name_origin=de:05774:7268&outputFormat=rapidJSON&ptOptionsActive=1&routeType=LEASTTIME&serverInfo=1&sl3plusTripMacro=1&trITMOTvalue100=10&type_destination=any&type_notVia=any&type_origin=any&type_via=any&useElevationData=1&useProxFootSearch=true&useRealtime=1&useUT=1&version=10.6.14.22&vrrTripMacro=1"
    # response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.text)
        if save:
            with open("latest_trip_response.json", "wb") as file:
                file.write(response.content)
        return TripResponse(**data)
    else:
        print(f"Trip Error: {origin}, {destination}: {response.status_code}")
        return None


def print_trip(trip: TripResponse):
    if trip is None:
        print("/n### ERROR ###")
        print("trip is NONE")
        print("---/n")
        return
    if not trip.journeys:
        print("/n### ERROR ###")
        for msg in trip.systemMessages:
            print(msg.text)
        print("---/n")
        return

    for idx, journey in enumerate(trip.journeys):
        n_legs = len(journey.legs)

        if n_legs > 0:

            origin = journey.legs[0].origin.name
            destination = journey.legs[-1].destination.name

            departure = journey.legs[0].origin.departureTimePlanned
            arrival = journey.legs[-1].destination.arrivalTimePlanned

            duration = arrival - departure
            minutes = int(duration.total_seconds() // 60)

            print(f"Journey {idx + 1}:")
            print(f"  von : {origin}")
            print(f"  nach: {destination}")
            print(
                f"  🕒 Abfahrt: {departure.astimezone(ZoneInfo("Europe/Berlin")).strftime('%H:%M')}"
            )
            print(
                f"  🕒 Ankunft: {arrival.astimezone(ZoneInfo("Europe/Berlin")).strftime('%H:%M')}"
            )
            print(f"  ⏳ Dauer  : {minutes} min")
            print(f"  🔀 Umstiege: {journey.interchanges}")
            print("-" * 40)

        else:
            print(f"Journey {idx + 1}: Keine Legs.")


def toCoordinateString(coords: list[float]) -> str:
    return f"{coords[0]}:{coords[1]}:WGS84[dd.ddddddddd]"


def toTripResult(
    origin_coords: list[float],
    origin_stop: str,
    dest_name: str,
    dest_coords: list[float],
    dest_stop: str,
    fid: int,
    props: Properties,
    trip: TripResponse,
) -> TripResult:

    return TripResult(
        origin=origin_coords,
        origin_stop=origin_stop,
        destination_name=dest_name,
        destination=dest_coords,
        destination_stop=dest_stop,
        fid=fid,
        properties=props,
        trip=trip,
    )


def getTrip(
    date: str,
    time: str,
    feature: Feature,
    dest_name: str,
    dest_coords: list[float],
    dest_stop: str,
) -> TripResult:

    origin_coords = feature.geometry.coordinates
    fid = feature.properties.fid

    # fetch origin stops
    origin_stops = fetch_stops(toCoordinateString(origin_coords))
    if len(origin_stops.locations) > 0:
        origin_nearest_stop = origin_stops.locations[0].assignedStops[0].id

        print("fetching Origin id: " + origin_nearest_stop)

        # fetch trips
        trip_data = fetch_trips(
            date=date,
            time=time,
            origin=origin_nearest_stop,
            destination=dest_stop,
            save=True,
        )
    else:
        origin_nearest_stop = "undefined"
        trip_data = None

    print("done: fetching Origin id: " + origin_nearest_stop)

    # print_trip(trip_data)
    result = toTripResult(
        origin_coords,
        origin_nearest_stop,
        dest_name,
        dest_coords,
        dest_stop,
        fid,
        feature.properties,
        trip_data,
    )
    return result


def saveTripResult(ts: TripResult, file_name: Path):
    with open(str(file_name), "w", encoding="utf-8") as file:
        file.write(ts.to_json())


def processPtFeatures(
    features: list[Feature],
    dest_name: str,
    dest_coords: list[float],
    date: str,
    time: str,
):
    # clear target dir
    base_path = Path(__file__).parent.parent
    target_dir = base_path / "trips"
    
    shutil.rmtree(target_dir)

    dest_stops = fetch_stops(toCoordinateString(dest_coords))
    dest_stop_id = dest_stops.locations[0].assignedStops[0].id

    print(f"start processing {len(features)} features.")
    use_executor = True
    if use_executor:
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(
                lambda f: processFeature(
                    f, date, time, dest_name, dest_coords, dest_stop_id
                ),
                features,
            )
    else:
        for i in range(0, len(features)):
            f = features[i]
            processFeature(f, date, time, dest_name, dest_coords, dest_stop_id)


def processFeature(
    f: Feature,
    date: str,
    time: str,
    dest_name: str,
    dest_coords: str,
    dest_stop_id: str,
):
    base_path = Path(__file__).parent.parent
    target_dir = base_path / "trips"
    target_dir.mkdir(parents=True, exist_ok=True)

    file_name = target_dir / f"fid_{f.properties.fid}.json"

    if not file_name.exists():
        tripResult = getTrip(date, time, f, dest_name, dest_coords, dest_stop_id)
        saveTripResult(tripResult, file_name)
        # print_trip(tripResult.trip)


def runBatch(origins_file_name, dest_name, dest_coords, data, arrival_time):
    # Point feature layer in GEOJSON
    # NOTE: crs must be 4326!!!
    with open(origins_file_name) as f:
        data = json.load(f)
    wgc = PtGeoJSON(**data)

    print(f"#origin = {len(wgc.features)}")

    processPtFeatures(wgc.features, dest_name, dest_coords, date, arrival_time)
    convertBatch("trips", "hx_geotrips_" + str(int(time.time())))


if __name__ == "__main__":

    origins_file_name = "le_clc_centroids_4326.geojson"

    # Lemgo
    dest_name = "TH OWL Lemgo"
    dest_coords = [8.904567814531946, 52.016971746079157]
    print(f"destination = {dest_name}")
    # Detmold
    # dest_name = "TH OWL Detmold"
    # dest_coords = [8.86613299901934, 51.9365590024518]

    # Hoexter
    # dest_name = "TH OWL Hoexter"
    # dest_coords = [9.3703414708828, 51.7836904046917]

    date = "06.05.2025"
    arrival_time = "08:00"

    runBatch(origins_file_name, dest_name, dest_coords, date, arrival_time )
