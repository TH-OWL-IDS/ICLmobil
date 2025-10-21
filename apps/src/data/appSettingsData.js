/*
 * Copyright 2025 Sascha Martinetz - Fraunhofer IOSB-INA
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const AppSettingsData = 
{ 
    APP_VERSION: 'v2.8.2',
    API_HOSTS: {
        development: "https://dev1.iclmobil.g.iplus1.de",
        production: "https://prod.iclmobil.g.iplus1.de"
    },
    API_URL: "/api/v1",
    API_IMAGE_URL: "/file/v1/user/getProfileImage",

    FAST_START_OPTIONS: [
        {
            id: 0,
            type: 'own_scooter',
            string: {
                de:  'Eigener Scooter',
                en:  'Own Scooter'
            }
        },
        {
            id: 1,
            type: 'own_bike',
            string: {
                de:  'Eigenes Bike',
                en:  'Own Bike'
            }
        },
        {
            id: 2,
            type: 'walk',
            string: {
                de:  'Fußweg',
                en:  'Footwalk'
            }
        }
    ],

    MAPBOX_API: '',
    MAPBOX_TOKEN: '',
    MAPBOX_DRIVING_URI: '',
    MAPBOX_WALKING_URI: '',
    MAPBOX_CYCLING_URI: '',
    MAPBOX_PLACES_URI: '',
    MAPBOX_STYLE: '',
    MAPBOX_BBOX_COORDS: [],

    POOLING_DOWNLOAD_URLS: {
        development: '',
        production: ''
    },
    POOLING_URLS: {
        development: '',
        production: ''
    },
    POOLING_REGISTER: '',
    POOLING_PLANNED_DRIVER: '',
    POOLING_PREVIOUS_DRIVER: '',
    POOLING_PLANNED_PASSENGER: '',
    POOLING_PREVIOUS_PASSENGER: '',
    POOLING_RIDE_OFFER: ''
}

export { AppSettingsData };