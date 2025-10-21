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
              class="startedRide">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar">
            <div class="left sheet-title">
                {{ title }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet" data-cy="startedride-close-btn">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-page-content>
            <f7-block class="no-padding-top no-margin-top">
                <div class="grid grid-cols-1">
                    <div style="text-align: center"><img :src="titleBanner" style="max-width: 70%; height: auto;"/></div>
                </div>

                <f7-button
                    href="#"
                    v-if="localRide.type === 'sharing'"
                    @click="unlockAsset"
                    :disabled="unlockLoading"
                    data-cy="startedride-unlockvehicle-btn"
                    fill
                    large
                    style="--f7-button-large-text-transform: none"
                >
                    <f7-preloader v-if="unlockLoading" size="20px" style="margin-right: 8px;" />
                    <div v-if="localRide.vehicle_type.en === 'Bike' && !unlockLoading">
                        {{ $t('activity.sheet.startedride.button.unlock-bike') }}
                    </div>
                    <div v-else-if="!unlockLoading">
                        {{ $t('activity.sheet.startedride.button.unlock-scooter') }}
                    </div>
                </f7-button>

                <div class="button-wrapper" v-if="localRide.type === 'sharing'">
                    <f7-button 
                        href="#" 
                        @click="lockAsset" 
                        :disabled="lockLoading" 
                        data-cy="startedride-lockvehicle-btn"
                        fill 
                        large 
                        style="background-color: #FF5522 !important; --f7-button-large-text-transform: none"
                    >
                        <f7-preloader v-if="lockLoading" size="20px" style="margin-right: 8px;" />
                        <div v-if="localRide.vehicle_type.en === 'Bike' && !lockLoading">
                            {{ this.$t('activity.sheet.startedride.button.lock-bike') }}
                        </div>
                        <div v-else-if="!lockLoading">
                            {{ this.$t('activity.sheet.startedride.button.lock-scooter') }}
                        </div>
                    </f7-button>
                </div>

                <div v-if="localRide.type == 'sharing'" class="button-wrapper-top">
                    <f7-button href="#" @click="showInstructions" data-cy="startedride-showinstructions-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.startedride.button.instructions') }}</f7-button>
                </div>

                <div v-if="localRide.type != 'rriveUse'" class="button-wrapper">
                    <f7-button href="#" @click="handleEndRide" data-cy="startedride-endride-btn" fill large style="background-color: #4488FF !important; --f7-button-large-text-transform: none">
                        <f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;
                        <div v-if="localRide.type === 'walk'">{{ this.$t('activity.sheet.startedride.button.end-walk') }}</div>
                        <div v-else>{{ this.$t('activity.sheet.startedride.button.end-ride') }}</div>
                    </f7-button>
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
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.startedride.when') }}</td>
                                <td>{{ localRide.rideDate }} - {{ localRide.rideTime }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.startedride.ridestart') }}</td>
                                <td><div v-html="localRide.rideStart"></div></td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.startedride.ridedestination') }}</td>
                                <td><div v-html="localRide.rideDestination"></div></td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.startedride.departure') }}</td>
                                <td>{{ this.$t('activity.sheet.startedride.approximate') }} {{ localRide.rideTime }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.startedride.arrival') }}</td>
                                <td>{{ this.$t('activity.sheet.startedride.approximate') }} {{ localRide.approxTimeOfArrival }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div v-if="localRide.type == 'pt'" class="button-wrapper-bottom">
                    <f7-button href="#" @click="takeMeToTicket" data-cy="startedride-gototicket-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.startedride.button.buy-ticket') }}</f7-button>
                </div>

                <div v-if="localRide.type == 'rriveUse'" class="button-wrapper-bottom">
                    <f7-button href="#" @click="takeMeToCarPool" data-cy="startedride-gotocarpool-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.startedride.button.takemetopool') }}</f7-button>
                </div>

                <div class="map-wrapper">
                    <div ref="mapContainer" class="map-container"></div>
                </div>

                <div class="button-wrapper-top">
                    <f7-button href="#" @click="takeMeThere" data-cy="startedride-gotoride-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.startedride.button.takemethere') }}</f7-button>
                </div>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page-content>
    </f7-sheet>

    <ImagePicker ref="imagePicker"/>
    <Dialog ref="dialogComponent"/>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';

    import ImagePicker from './imagePicker.vue';
    import Dialog from '../components/dialog_points.vue';

    import scooter from "../assets/placeholder/images/scooter.png";
    import bike from "../assets/placeholder/images/bike.png";
    import bus from "../assets/placeholder/images/bus.png";
    import car from "../assets/placeholder/images/car.png";
    import walk from "../assets/placeholder/images/walk.png";

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
            ImagePicker,
            Dialog
        },
        data() {
            return {
                title: this.$t('activity.sheet.startedride.title'),
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
                directionsEnd: [],
                locale: this.$store.getters.getAppLocaleString,
                userGeolocation: { latitude: null, longitude: null },
                unlockLoading: false,
                unlockTimeout: null,
                unlockTimeoutTime: 10000,
                lockLoading: false,
                lockTimeout: null,
                lockTimeoutTime: 10000
            };
        },
        computed: {
            inAppBrowser() {
                return this.$store.getters.getPluginInAppBrowser;
            },
            geolocation() {
                return this.$store.getters.getPluginGeolocation;
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        created() {
            this.emitter.on('set-started-ride-data', (ride) => {
                this.localRide = { ...ride };
                this.changeBanner(this.localRide.rideIcon);
            });
        },
        methods: {
            init() {
                console.log("SHEET STARTED RIDE OPENED");
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
                        this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
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
                    if (this.localRide.source_link_more_information) {
                        const ticketURL = this.localRide.source_link_more_information;
                        if (this.inAppBrowser) {
                            if (f7.device.cordova) {
                                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
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
            endRide() {
                try {
                    this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                    f7.dialog.confirm(this.$t('activity.sheet.startedride.dialog.confirm-end-ride'), async () => {
                        let data = {
                            trip_mode: this.localRide.type,
                            state: "finished",
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

                        if (this.localRide.type === 'sharing') {
                            if (f7.device.cordova) {
                                this.geolocation.getCurrentPosition((position) => {
                                    this.userGeolocation = { latitude: position.coords.latitude, longitude: position.coords.longitude }
                                }, (error) => {
                                    console.log("GEOLOCATION ERROR: ", error)
                                });

                                let message = `<div class="dialog-icon-container">
                                                <i class="f7-icons dialog-icon">checkmark_alt_circle</i>
                                               </div>` + 
                                                this.$t('app.dialog.success.asset-locked') + `<br/><br/>`+
                                                this.$t('activity.sheet.startedride.dialog.take-image');

                                f7.dialog.confirm(message, async () => {
                                    this.takeImage(this.userGeolocation, this.localRide.id);
                                });
                            }
                        }
                        
                        const response = await bookingService.updateBooking(this.localRide.id, data);
                        const responsePoints = await bookingService.getBooking(this.localRide.id);
                        if (response.msg) {
                            if (responsePoints.data) {
                                let pointsFloored = Math.floor(responsePoints.data.score_points);
                                if (pointsFloored > 0) {
                                    this.emitter.emit('show-confetti', { emojis: false, poop: false });
                                } else {
                                    this.emitter.emit('show-confetti', { emojis: true, poop: true });
                                }
                                this.$refs.dialogComponent.showDialog(pointsFloored);
                            }
                            this.emitter.emit('refresh-booking-list', '');
                            this.closeSheet();
                        } else if (response.error) {
                            f7.toast.show({
                                text: this.$t('app.dialog.error.ride-end'),
                                icon: theme.ios
                                ? '<i class="f7-icons">exclamationmark_triangle</i>'
                                : '<i class="material-icons">error</i>',
                                position: 'center',
                                closeTimeout: 2000,
                                destroyOnClose: true
                            });
                        }
                    })
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            handleEndRide() {
                if (this.localRide.type === 'sharing') {
                    f7.dialog.alert(
                        this.getVehicleUserHintEndHtml(),
                        this.$t('activity.sheet.startedride.dialog.instructions-title'),
                        () => {
                            this.endRide();
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
                    this.endRide();
                }
            },
            async unlockAsset() {
                try {
                    if (this.unlockLoading) return;
                    this.unlockLoading = true;
                    this.unlockTimeout = setTimeout(() => {
                        this.unlockLoading = false;
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.timeout'), this.$t('app.dialog.error.title'));
                    }, this.unlockTimeoutTime);

                    let data = null;
                    if (this.localRide.vehicle_unlock_secret_needed) {
                        let hint = this.localRide.vehicle_unlock_secret_user_hint[this.locale] || this.localRide.vehicle_unlock_secret_user_hint.de;
                        f7.dialog.prompt(hint, (secret) => {
                            if (!secret || !secret.trim()) {
                                this.unlockLoading = false;
                                clearTimeout(this.unlockTimeout);
                                return;
                            }
                            data = {
                                booking_id: this.localRide.id,
                                unlock_secret: secret
                            };
                            this.unlock(data);
                        });
                    } else {
                        data = {
                            booking_id: this.localRide.id
                        };
                        this.unlock(data);
                    }
                } catch(err) {
                    this.unlockLoading = false;
                    clearTimeout(this.unlockTimeout);
                    console.log("ERROR: ", err)
                }
            },
            async unlock(data) {
                try {
                    const response = await assetService.assetUnlock(data);
                    clearTimeout(this.unlockTimeout);
                    this.unlockLoading = false;
                    if (response.status === 200) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        f7.toast.show({
                            text: this.$t('app.dialog.success.asset-unlocked'),
                            icon: theme.ios
                                ? '<i class="f7-icons">checkmark_alt_circle</i>'
                                : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                    } else if (response.status === 400) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        let hint = response.data.error[this.locale] || response.data.error.de;
                        f7.dialog.alert(hint, this.$t('app.dialog.error.title'));
                    } else if (response.status === 401) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.not-authorized'), this.$t('app.dialog.error.title'));
                    }
                } catch(err) {
                    clearTimeout(this.unlockTimeout);
                    this.unlockLoading = false;
                    console.log("ERROR: ", err)
                }
            },
            async lockAsset() {
                try {
                    if (this.lockLoading) return;
                    this.lockLoading = true;
                    this.lockTimeout = setTimeout(() => {
                        this.lockLoading = false;
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.timeout'), this.$t('app.dialog.error.title'));
                    }, this.lockTimeoutTime);

                    let data = {
                        booking_id: this.localRide.id
                    };
                    const response = await assetService.assetLock(data);
                    clearTimeout(this.lockTimeout);
                    this.lockLoading = false;
                    if (response.status === 200) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        f7.toast.show({
                            text: this.$t('app.dialog.success.asset-locked'),
                            icon: theme.ios
                                ? '<i class="f7-icons">checkmark_alt_circle</i>'
                                : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                    } else if (response.status === 400) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.bad-request'), this.$t('app.dialog.error.title'));
                    } else if (response.status === 401) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.not-authorized'), this.$t('app.dialog.error.title'));
                    }
                } catch(err) {
                    clearTimeout(this.lockTimeout);
                    this.lockLoading = false;
                    console.log("ERROR: ", err)
                }
            },
            showInstructions() {
                try {
                    f7.dialog.alert(
                        this.getVehicleUserHintEndHtml(),
                        this.$t('activity.sheet.startedride.dialog.instructions-title')
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
            getVehicleUserHintEndHtml() {
                return this.localRide.vehicle_user_hint_start?.[this.$i18n.locale] || '';
            },
            takeImage(geolocation, id) {
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
                this.$refs.imagePicker.takeImageProof(geolocation, id);
            },
            closeSheet() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close('.startedRide');
            },
            openLink(link) {
                if (this.inAppBrowser) {
                    if (f7.device.cordova) {
                        this.inAppBrowser.open(link, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                    }
                }
            },
            sendHapticFeedback(androidType, iosType) {
                if (this.hapticFeedback) {
                    this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                        console.error("HAPTIC ERROR: ", error);
                    });
                }
            }
        },
        beforeUnmount() {
            this.emitter.off('set-started-ride-data');
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