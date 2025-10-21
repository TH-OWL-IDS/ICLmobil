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
 
<template>
    <f7-sheet @sheet:opened="init"
              @sheet:closed="onClose"
              swipe-handler=".swipe-handler" 
              style="min-height: 90vh" 
              swipe-to-close
              push
              backdrop
              :close-by-backdrop-click="false" 
              :close-by-outside-click="false" 
              class="nextRide">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar">
            <div class="left sheet-title">
                {{ title }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet('.nextRide')" data-cy="nextride-close-btn">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-page-content>
            <f7-block class="no-padding-top no-margin-top">
                <div class="grid grid-cols-1">
                    <div style="text-align: center"><img :src="titleBanner" style="max-width: 70%; height: auto;"/></div>
                </div>

                <f7-button v-if="localRide.type != 'rriveUse'" href="#" @click="handleStartRide" data-cy="nextride-startride-btn" fill large style="--f7-button-large-text-transform: none">
                    <div v-if="localRide.type === 'walk'">{{ this.$t('activity.sheet.nextride.button.startwalk') }}</div>
                    <div v-else>{{ this.$t('activity.sheet.nextride.button.startride') }}</div>
                </f7-button>

                <div v-if="localRide.type == 'sharing'" class="button-wrapper-top">
                    <f7-button href="#" @click="showInstructions" data-cy="nextride-showinstructions-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.nextride.button.instructions') }}</f7-button>
                </div>

                <div v-if="localRide.type == 'rriveUse'">
                    <f7-button href="#" @click="takeMeToCarPool" data-cy="nextride-gotocarpool-btn" fill large style="--f7-button-large-text-transform: none">{{ this.$t('activity.sheet.nextride.button.takemetopool') }}</f7-button>
                </div>

                <div class="button-wrapper-top">
                    <f7-button href="#" @click="takeMeThere" data-cy="nextride-gotoride-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.nextride.button.takemethere') }}</f7-button>
                </div>

                <div v-if="localRide.type == 'pt'" class="button-wrapper-bottom">
                    <f7-button href="#" @click="takeMeToTicket" data-cy="nextride-gototicket-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.nextride.button.buy-ticket') }}</f7-button>
                </div>

                <div class="data-table">
                    <table>
                        <tbody>
                            <tr v-if="localRide.type == 'sharing'">
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.vehicle-model') }}</td>
                                <td>{{ localRide.vehicle_model }}</td>
                            </tr>
                            <tr v-if="localRide.type == 'sharing'">
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.vehicle-number') }}</td>
                                <td>{{ localRide.vehicle_number }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.when') }}</td>
                                <td>{{ localRide.rideDate }} - {{ localRide.rideTime }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.ridestart') }}</td>
                                <td><div v-html="localRide.rideStart"></div></td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.ridedestination') }}</td>
                                <td><div v-html="localRide.rideDestination"></div></td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.departure') }}</td>
                                <td>{{ this.$t('activity.sheet.nextride.approximate') }} {{ localRide.rideTime }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.nextride.arrival') }}</td>
                                <td>{{ this.$t('activity.sheet.nextride.approximate') }} {{ localRide.approxTimeOfArrival }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="map-wrapper">
                    <div ref="mapContainer" class="map-container"></div>
                </div>
                <div v-if="localRide.type == 'rriveUse'" class="button-wrapper">
                    <f7-button href="#" @click="cancelCarPool" data-cy="nextride-cancel-btn" fill large style="background-color: #FF0000 !important; --f7-button-large-text-transform: none"><f7-icon ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>&nbsp;{{ this.$t('activity.sheet.nextride.button.cancelbooking') }}</f7-button>
                </div>
                <div v-else class="button-wrapper">
                    <f7-button href="#" @click="cancelBooking" data-cy="nextride-cancel-btn" fill large style="background-color: #FF0000 !important; --f7-button-large-text-transform: none"><f7-icon ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>&nbsp;{{ this.$t('activity.sheet.nextride.button.cancelbooking') }}</f7-button>
                </div>
            </f7-block>
            
            <div class="page-padding"></div>
        </f7-page-content>
    </f7-sheet>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';

    import scooter from "../assets/placeholder/images/scooter.png";
    import bike from "../assets/placeholder/images/bike.png";
    import bus from "../assets/placeholder/images/bus.png";
    import car from "../assets/placeholder/images/car.png";
    import walk from "../assets/placeholder/images/walk.png";
    import helmet from "../assets/placeholder/images/helmet.png";

    import mapboxgl from 'mapbox-gl';
    import '../../node_modules/mapbox-gl/dist/mapbox-gl.css';
    import axios from 'axios';

    import bookingService from '../services/bookingService';
    import assetService from '../services/assetService';
  
    export default {
        components: {
            f7,
            f7ready,
            f7Page,
            f7Block,
            f7Link,
            Map,
        },
        data() {
            return {
                title: this.$t('activity.sheet.nextride.title'),
                titleBanner: scooter,
                accessToken: this.$store.getters.getMapboxToken,
                mapboxAPI: this.$store.getters.getMapboxApi,
                mapboxCyclingURI: this.$store.getters.getMapboxCyclingURI,
                mapboxWalkingURI: this.$store.getters.getMapboxWalkingURI,
                mapboxDrivingURI: this.$store.getters.getMapboxDrivingURI,
                poolingPlannedPassengerURL: this.$store.getters.getPoolingPlannedPassenger,
                map: null,
                localRide: {},
                directionsStart: [],
                directionsEnd: []
            };
        },
        computed: {
            inAppBrowser() {
                return this.$store.getters.getPluginInAppBrowser;
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        created() {
            this.emitter.on('set-next-ride-data', (ride) => {
                this.localRide = { ...ride };
                this.changeBanner(this.localRide.rideIcon);
            });
        },
        methods: {
            init() {
                console.log("SHEET NEXT RIDE OPENED");
                this.drawMap();
                console.log("LOCAL RIDE: ", this.localRide)
            },
            onClose() {
                console.log("SHEET CLOSING")
                this.map.remove();
                this.map = null;
            },
            drawMap() {
                mapboxgl.accessToken = this.accessToken;
                const map = new mapboxgl.Map({
                    container: this.$refs.mapContainer,
                    style: this.$store.getters.getMapboxStyle,
                    center: [8.90500, 52.01750],
                    zoom: 13,
                    minZoom: 10,
                });

                this.map = map;

                map.on('load', () => {
                    this.map.resize();
                    // this.getDirectionsFromAddresses('Campusallee 19, 32657 Lemgo', 'Mittelstraße 34, 32657 Lemgo');
                    // this.getDirections([8.90500, 52.01750], [8.89250, 52.02600]);
                    const directionsStart = [this.localRide.rideStartLongitude, this.localRide.rideStartLatitude];
                    const directionsEnd = [this.localRide.rideDestinationLongitude, this.localRide.rideDestinationLatitude];
                    this.getDirections(directionsStart, directionsEnd);
                });
            },
            async getDirections(start, end) {
                try {
                    let url = `${this.mapboxAPI}${this.mapboxDrivingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;

                    switch(this.localRide.type) {
                        case "scooter":
                        case "bike":
                        case "own_scooter":
                        case "own_bike":
                            url = `${this.mapboxAPI}${this.mapboxCyclingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
                            break;
                        case "walk":
                            url = `${this.mapboxAPI}${this.mapboxWalkingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
                            break;
                        default:
                            break;
                    }

                    const response = await axios.get(url);
                    const data = response.data;

                    const route = data.routes[0].geometry;

                    this.map.addSource('route', {
                        type: 'geojson',
                        data: {
                            type: 'Feature',
                            properties: {},
                            geometry: route,
                        },
                    });

                    this.map.addLayer({
                        id: 'route',
                        type: 'line',
                        source: 'route',
                        layout: {
                            'line-join': 'round',
                            'line-cap': 'round',
                        },
                        paint: {
                            'line-color': '#3b9ddd',
                            'line-width': 5,
                        },
                    });

                    new mapboxgl.Marker({ color: 'green' })
                        .setLngLat(start)
                        .addTo(this.map);

                    new mapboxgl.Marker({ color: 'red' })
                        .setLngLat(end)
                        .addTo(this.map);

                    const coordinates = route.coordinates;
                    const bounds = coordinates.reduce((b, coord) => b.extend(coord), new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));

                    this.map.fitBounds(bounds, {
                        padding: 60,
                        maxZoom: 15,
                    });
                } catch (error) {
                    console.error('Error fetching directions:', error);
                }
            },
            takeMeThere() {
                try {
                    this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                    let directionsStart = [];
                    let directionsEnd = [];
                    let googleMapsUrl = '';
                    let appleMapsUrl = '';

                    if (this.localRide.type == 'rriveUse' || this.localRide.type == 'pt') {
                        directionsStart = [this.localRide.rideStartLatitude, this.localRide.rideStartLongitude];
                        googleMapsUrl = `geo:${directionsStart.join(',')}?q=${directionsStart.join(',')}&dir_action=walking`;
                        appleMapsUrl = `maps://?q=${directionsStart.join(',')}&dirflg=d&t=w`;
                        console.log("googleMapsUrl: ", googleMapsUrl)
                        console.log("appleMapsUrl: ", appleMapsUrl)
                    } else if (this.localRide.type == 'sharing') {
                        directionsStart = [this.localRide.vehicle_location_latitude, this.localRide.vehicle_location_longitude];
                        googleMapsUrl = `geo:${directionsStart.join(',')}?q=${directionsStart.join(',')}&dir_action=walking`;
                        appleMapsUrl = `maps://?q=${directionsStart.join(',')}&dirflg=d&t=w`;
                        console.log("googleMapsUrl: ", googleMapsUrl)
                        console.log("appleMapsUrl: ", appleMapsUrl)
                    } else {
                        directionsStart = [this.localRide.rideStartLatitude, this.localRide.rideStartLongitude];
                        directionsEnd = [this.localRide.rideDestinationLatitude, this.localRide.rideDestinationLongitude];

                        googleMapsUrl = `geo:${directionsStart.join(',')}?q=${directionsEnd.join(',')}`;
                        appleMapsUrl = `maps://?saddr=${directionsStart.join(',')}&daddr=${directionsEnd.join(',')}`;
                    }

                    if (this.inAppBrowser) {
                        if (f7.device.ios) {
                            this.inAppBrowser.open(appleMapsUrl, '_system');
                        } else if (f7.device.android) {
                            this.inAppBrowser.open(googleMapsUrl, '_system');
                        }
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            takeMeToTicket() {
                try {
                    this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                    if (this.localRide.source_link_more_information) {
                        const ticketURL = this.localRide.source_link_more_information;
                        if (this.inAppBrowser) {
                            if (f7.device.cordova) {
                                this.inAppBrowser.open(ticketURL, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                            }
                        }
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            takeMeToCarPool() {
                try {
                    this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                    if (this.localRide.provider_id) {
                        const url = this.poolingPlannedPassengerURL + this.localRide.provider_id;
                        if (this.inAppBrowser) {
                            if (f7.device.cordova) {
                                this.inAppBrowser.open(url, '_system');
                            }
                        }
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            changeBanner(icon) {
                switch(icon) {
                    case "pedal_bike":
                        this.titleBanner = bike;
                        break;
                    case "directions_bus":
                        this.titleBanner = bus;
                        break;
                    case "directions_car":
                        this.titleBanner = car;
                        break;
                    case "directions_walk":
                        this.titleBanner = walk;
                        break;
                    default:
                        this.titleBanner = scooter;
                        break;
                }
            },
            cancelBooking() {
                try {
                    this.sendHapticFeedback('CONFIRM', 'ImpactHeavy');
                    f7.dialog.confirm(this.$t('activity.sheet.nextride.dialog.confirmCancelText'), async () => {
                        let data = {
                            trip_mode: this.localRide.type,
                            state: "canceled",
                            from_location_latitude: this.localRide.rideStartLatitude,
                            from_location_longitude: this.localRide.rideStartLongitude,
                            from_description: this.localRide.rideStart,
                            to_location_latitude: this.localRide.rideDestinationLatitude,
                            to_location_longitude: this.localRide.rideDestinationLongitude,
                            to_description: this.localRide.rideDestination,
                            start_time: this.localRide.rideStartTimestamp,
                            end_time: this.localRide.rideEndTimestamp,
                            vehicle_id: this.localRide.vehicle_id
                        };
                        const response = await bookingService.updateBooking(this.localRide.id, data);
                        if (response.msg) {
                            this.sendHapticFeedback('CONFIRM', 'Success');
                            f7.dialog.alert(this.$t('app.dialog.success.ride-cancel'), this.$t('app.dialog.success.title'));
                            this.emitter.emit('refresh-booking-list', '');
                            this.closeSheet();
                        } else if (response.error) {
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('app.dialog.error.ride-cancel'), this.$t('app.dialog.error.title'));
                            this.closeSheet();
                        }
                    })
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            cancelCarPool() {
                try {
                    this.sendHapticFeedback('CONFIRM', 'ImpactHeavy');
                    if (this.localRide.provider_id) {
                        const url = this.poolingPlannedPassengerURL + this.localRide.provider_id + '/deactivate/';
                        if (this.inAppBrowser) {
                            if (f7.device.cordova) {
                                this.inAppBrowser.open(url, '_system');
                            }
                        }
                        this.closeSheet();
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            async startRide() {
                try {
                    let data = {
                        trip_mode: this.localRide.type,
                        state: "started",
                        from_location_latitude: this.localRide.rideStartLatitude,
                        from_location_longitude: this.localRide.rideStartLongitude,
                        from_description: this.localRide.rideStart,
                        to_location_latitude: this.localRide.rideDestinationLatitude,
                        to_location_longitude: this.localRide.rideDestinationLongitude,
                        to_description: this.localRide.rideDestination,
                        start_time: this.getStarttime(),
                        end_time: this.localRide.rideEndTimestamp,
                        vehicle_id: this.localRide.vehicle_id
                    };
                    const response = await bookingService.updateBooking(this.localRide.id, data);
                    if (response.msg) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        f7.toast.show({
                            text: this.$t('app.dialog.success.ride-start'),
                            icon: theme.ios
                            ? '<i class="f7-icons">checkmark_alt_circle</i>'
                            : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                        this.emitter.emit('refresh-booking-list', '');
                        this.closeSheet();
                        if (this.localRide.type == 'rriveUse') {
                            this.takeMeToCarPool();
                        } else if (this.localRide.type == 'sharing') {
                            this.emitter.emit('open-started-ride', this.localRide);
                        }
                    } else if (response.error) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.toast.show({
                            text: this.$t('app.dialog.error.ride-start'),
                            icon: theme.ios
                            ? '<i class="f7-icons">exclamationmark_triangle</i>'
                            : '<i class="material-icons">error</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            handleStartRide() {
                if (this.localRide.type === 'sharing') {
                    f7.dialog.alert(
                        this.getVehicleUserHintStartHtml(),
                        this.$t('activity.sheet.nextride.dialog.safety-instructions-title'),
                        () => {
                            this.startRide();
                        }
                    );
                    this.$nextTick(() => {
                        setTimeout(() => {
                            const dialogEl = document.querySelector('.dialog .locker-link');
                            if (dialogEl) {
                                dialogEl.addEventListener('click', (e) => {
                                    e.preventDefault();
                                    this.openLink(dialogEl.getAttribute('href'));
                                });
                            }
                        }, 100);
                    });
                } else {
                    this.startRide();
                }
            },
            async unlockAsset() {
                try {
                    let data = {
                        booking_id: this.localRide.id,
                        unlock_secret: "bibidibabediboo"
                    };
                    const response = await assetService.assetUnlock(data);
                    if (response.status === 200) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        f7.dialog.alert(this.$t('app.dialog.success.asset-unlocked'), this.$t('app.dialog.success.title'));
                    } else if (response.status === 400) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.bad-request'), this.$t('app.dialog.error.title'));
                    } else if (response.status === 401) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.not-authorized'), this.$t('app.dialog.error.title'));
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            async lockAsset() {
                try {
                    let data = {
                        booking_id: this.localRide.id
                    };
                    const response = await assetService.assetLock(data);
                    if (response.status === 200) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        f7.dialog.alert(this.$t('app.dialog.success.asset-locked'), this.$t('app.dialog.success.title'));
                    } else if (response.status === 400) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.bad-request'), this.$t('app.dialog.error.title'));
                    } else if (response.status === 401) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.not-authorized'), this.$t('app.dialog.error.title'));
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            getStarttime() {
                const now = new Date();
                return now.toISOString();
            },
            showInstructions() {
                try {
                    f7.dialog.alert(
                        this.getVehicleUserHintStartHtml(),
                        this.$t('activity.sheet.nextride.dialog.safety-instructions-title')
                    );
                    this.$nextTick(() => {
                        setTimeout(() => {
                            const dialogEl = document.querySelector('.dialog .locker-link');
                            if (dialogEl) {
                                dialogEl.addEventListener('click', (e) => {
                                    e.preventDefault();
                                    this.openLink(dialogEl.getAttribute('href'));
                                });
                            }
                        }, 100);
                    });
                } catch(err) {
                    console.log("ERROR: ", err);
                }
            },
            closeSheet(sheet) {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close(sheet);
            },
            openSheet(sheet) {
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactMedium");
                f7.sheet.open(sheet);
            },
            sendHapticFeedback(androidType, iosType) {
                if (this.hapticFeedback) {
                    this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                        console.error("HAPTIC ERROR: ", error);
                    });
                }
            },
            getVehicleUserHintStartHtml() {
                const hint = this.localRide.vehicle_user_hint_start?.[this.$i18n.locale] || '';
                return `
                    <div style="display: flex; justify-content: center; margin-bottom: 16px;">
                        <img src="${helmet}" width="128" height="128" alt="Helm">
                    </div>
                    ${hint}
                `;
            },
            openLink(link) {
                if (this.inAppBrowser) {
                    if (f7.device.cordova) {
                        this.inAppBrowser.open(link, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                    }
                }
            },
        },
        beforeUnmount() {
            this.emitter.off('set-next-ride-data');
        }
    };
</script>

<style scoped>
    .map-wrapper {
        display: flex;
        flex-direction: column;
        height: 220px;
        box-sizing: border-box;
    }
    .map-container {
        flex-grow: 1;
        width: 100%;
        box-sizing: border-box;
        position: relative;
    }
    .button-wrapper-top {
        padding-top: 20px;
        padding-bottom: 20px;
    }
    .button-wrapper-bottom {
        padding-bottom: 20px;
    }
    .button-wrapper {
        padding-top: 20px;
        padding-bottom: 20px;
    }
</style>