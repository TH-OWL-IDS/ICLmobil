# Configuration

These entries are expected:

## Key: `AppConfig`

Schema: `backend.api_v1.schemas.FrontendAppConfig`

Value:

```json
{
    "MAPBOX_API": "https://api.mapbox.com",
    "MAPBOX_BBOX_COORDS": [
        8.80576,
        51.975857,
        8.997129,
        52.104398
    ],
    "MAPBOX_CYCLING_URI": "/directions/v5/mapbox/cycling/",
    "MAPBOX_DRIVING_URI": "/directions/v5/mapbox/driving/",
    "MAPBOX_PLACES_URI": "/geocoding/v5/mapbox.places/",
    "MAPBOX_STYLE": "mapbox://styles/mapbox/streets-v12",
    "MAPBOX_TOKEN": "pk.e...no0-SA",
    "MAPBOX_WALKING_URI": "/directions/v5/mapbox/walking/",
    "POOLING_DOWNLOAD_URLS": {
        "development": "https://rrive.com/Home/IclTestApps",
        "production": "https://rrive.com/Home/App"
    },
    "POOLING_PLANNED_DRIVER": "/tab/2/trips/planned/offer/",
    "POOLING_PLANNED_PASSENGER": "/tab/2/trips/planned/booking/",
    "POOLING_PREVIOUS_DRIVER": "/tab/2/trips/past/offer/",
    "POOLING_PREVIOUS_PASSENGER": "/tab/2/trips/past/booking/",
    "POOLING_REGISTER": "/icl/",
    "POOLING_RIDE_OFFER": "/tab/1/rideoffer/",
    "POOLING_URLS": {
        "development": "https://website-develop.rrive.com/dl-dev",
        "production": "https://rrive.com/dl"
    }
}
```