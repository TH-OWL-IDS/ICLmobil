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
    <f7-page :page-content="false">
      
        <NavBar ref="navBar" :title="title" :large="false" :showSearch="false" :showIcons="false" :showEdit="true"/>
        
        <f7-page :page-content="true">
            <Map 
                 ref="mapComponent" 
                 :search-query="searchQuery" 
                 @update-search-results="updateSearchResults" 
                 @marker-clicked-for-popover="handlePopoverTrigger"
                 @marker-clicked="handleMarkerClick"
            />
            <f7-popover class="marker-popover">
                <div class="wallet-main-icon-container">
                    <f7-icon color="gray" :material="destinationIcon" size="58"></f7-icon>
                </div>
                <div class="block-title block-title-nomargin block-title-medium text-align-left" >{{ this.$t('planning.popover.title') }}</div>
                <div class="popover-subtitle">{{ destinationOption }}</div>
                <div class="destinationTitle">{{ this.$t('planning.popover.subtitle') }}</div>
                <div class="destinationAddress">{{ destinationAdress }}</div>
                <div class="popover-button-wrapper">
                    <f7-button class="button-book" fill round @click="onBookClick">
                        <i class="f7-icons" style="font-size: 20px !important;">calendar_badge_plus</i>&nbsp;
                        {{ this.$t('planning.popover.button-book') }}
                    </f7-button>
                    <f7-button class="button-start" fill round @click="onStartClick">
                        <i class="f7-icons" style="font-size: 20px !important;">play_circle_fill</i>&nbsp;
                        {{ this.$t('planning.popover.button-ride') }}
                    </f7-button>
                </div>
            </f7-popover>
        </f7-page>

        <SheetLastLocations 
            ref="sheetLastLocations"
            :title="openLastLocationsTitle"
            @search="handleSearch" 
            @pickResult="handlePickResult"
            @pickFavorite="handlePickFavorite"
            @pickLastDestination="handlePickLastDestination"
            @update-search-query="handleSearch"
            :search-results="searchResults"
        />

        <RideOptions :title="rideOptionsTitle" />

        <BookRideCar :title="rideBookingTitle" />
        <BookRidePublicTransport :title="rideBookingTitle" />
        <BookRideShared :title="rideBookingTitle" />
        <BookRideFootWay :title="rideBookingTitle" />
        <BookRideOwnVehicle :title="rideBookingTitle" />

        <ToolBar ref="toolBar" :tabActive="tabActive"/>
    </f7-page>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link, theme } from 'framework7-vue';
    import $ from "dom7";

    import axios from 'axios';

    import NavBar from '../components/navbar.vue';
    import ToolBar from '../components/toolbar.vue';
    import SheetLastLocations from '../components/last_destinations.vue';
    import RideOptions from '../components/ride_options.vue';
    import BookRideCar from '../components/ride_booking_car.vue';
    import BookRideFootWay from '../components/ride_booking_foot_way.vue';
    import BookRidePublicTransport from '../components/ride_booking_public_transport.vue';
    import BookRideShared from '../components/ride_booking_shared.vue';
    import BookRideOwnVehicle from '../components/ride_booking_own_vehicle.vue';

    import bookingService from '../services/bookingService';

    import { formatTime } from '@/js/utilities/timeFormatter';

    import Map from '../components/map.vue';
    import '../../node_modules/mapbox-gl/dist/mapbox-gl.css';

    import loading from "../assets/icons/loading.gif";
    
    export default {
        components: {
            f7Page,
            f7Block,
            f7Tabs,
            f7Tab,
            f7Link,
            NavBar,
            ToolBar,
            Map,
            SheetLastLocations,
            RideOptions,
            BookRideCar,
            BookRideFootWay,
            BookRidePublicTransport,
            BookRideShared,
            BookRideOwnVehicle
        },
        data() {
            return {
                title: this.$t('planning.title'),
                accessToken: this.$store.getters.getMapboxToken,
                mapboxAPI: this.$store.getters.getMapboxApi,
                mapboxDrivingURI: this.$store.getters.getMapboxDrivingURI,
                mapboxCyclingURI: this.$store.getters.getMapboxCyclingURI,
                mapboxWalkingURI: this.$store.getters.getMapboxWalkingURI,
                openLastLocationsTitle: this.$t('planning.yourdestination'),
                tabActive: 2,
                rideOptionsTitle: this.$t('planning.yourride'),
                rideBookingTitle: this.$t('planning.bookride'),
                searchQuery: '',
                searchResults: [],
                destination: [],
                tripData: [],
                options: [],
                maxDistance: 150000,
                toastWaitLoading: null,
                destinationAdress: '',
                destinationOption: '',
                destinationIcon: '',
                destinationRideOption: null,
                currentDestination: null,
                selectedStartTime: null
            };
        },
        computed: {
            fastStartOptions: {
                get() {
                    return this.$store.getters.getFastStartOptions;
                }
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        mounted() {
            f7ready(async () => {
                this.showLastLocations = () => {
                    this.openLastDestinations();
                };
                this.hideLastLocations = () => {
                    this.closeLastDestinations();
                };
                this.showRideBookingCar = () => {
                    this.openRideBookingCar();
                };
                this.hideRideBookingCar = () => {
                    this.closeRideBookingCar();
                };
                this.showRideBookingFootWay = () => {
                    this.openRideBookingFootWay();
                };
                this.hideRideBookingFootWay = () => {
                    this.closeRideBookingFootWay();
                };
                this.showRideBookingHandlerPublicTransport = () => {
                    this.openRideBookingPublicTransport();
                };
                this.hideRideBookingHandlerPublicTransport = () => {
                    this.closeRideBookingPublicTransport();
                };
                this.showRideBookingHandlerShared = () => {
                    this.openRideBookingShared();
                };
                this.hideRideBookingHandlerShared = () => {
                    this.closeRideBookingShared();
                };
                this.showRideBookingHandlerOwnVehicle = () => {
                    this.openRideBookingOwnVehicle();
                };
                this.hideRideBookingHandlerOwnVehicle = () => {
                    this.closeRideBookingOwnVehicle();
                };
                this.showRideBookingHandlerCar = () => {
                    this.openRideBookingCar();
                };
                this.hideRideBookingHandlerCar = () => {
                    this.closeRideBookingCar();
                };
                this.showRideOptions = () => {
                    this.openRideOptions();
                };
                this.hideRideOptions = () => {
                    this.closeRideOptions();
                };

                this.emitter.on('showRideBookingFootWay', this.showRideBookingFootWay);
                this.emitter.on('hideRideBookingFootWay', this.hideRideBookingFootWay);
                this.emitter.on('showRideBookingPublicTransport', this.showRideBookingHandlerPublicTransport);
                this.emitter.on('hideRideBookingPublicTransport', this.hideRideBookingHandlerPublicTransport);
                this.emitter.on('showRideBookingShared', this.showRideBookingHandlerShared);
                this.emitter.on('hideRideBookingShared', this.hideRideBookingHandlerShared);
                this.emitter.on('showRideBookingOwnVehicle', this.showRideBookingHandlerOwnVehicle);
                this.emitter.on('hideRideBookingOwnVehicle', this.hideRideBookingHandlerOwnVehicle);
                this.emitter.on('showRideBookingCar', this.showRideBookingHandlerCar);
                this.emitter.on('hideRideBookingCar', this.hideRideBookingHandlerCar);
                this.emitter.on('showLastLocations', this.showLastLocations);
                this.emitter.on('hideLastLocations', this.hideLastLocations);
                this.emitter.on('showRideOptions', this.showRideOptions);
                this.emitter.on('hideRideOptions', this.hideRideOptions);

                this.emitter.emit('showLastLocations', '');

                this.emitter.emit('show-planning-tour');
            })
        },
        methods: {
            handleSearch(query) {
                const searchQuery = (query || '').toString().trim();
                this.searchQuery = searchQuery;
                if (searchQuery === '') {
                    this.searchResults = [];
                    return;
                }
                this.$refs.mapComponent.handleSearch(searchQuery);
            },
            handlePickResult(result) {
                if (!result) return;
                this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                this.$refs.mapComponent.handlePickResult(result);
            },
            handlePickFavorite(favorite) {
                if (!favorite) return;
                this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                this.$refs.mapComponent.handlePickFavorite(favorite);
            },
            handlePickLastDestination(lastDestination) {
                if (!lastDestination) return;
                this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                this.$refs.mapComponent.handlePickLastDestination(lastDestination);
            },
            updateSearchResults(results) {
                this.searchResults = [...results];
            },
            handlePopoverTrigger({ destination, rideOption, targetElement }) {
                this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                this.currentDestination = destination;
                
                if (destination.destPlaceName) {
                    const parts = destination.destPlaceName.split(', ');
                    if (parts.length > 1) {
                        parts.pop(); 
                        destination.destPlaceName = parts.join(', ');
                    }
                    this.destinationAdress = `${destination.destPlaceName}`;
                }
                
                if (rideOption && this.fastStartOptions) {
                    const matchedOption = this.fastStartOptions.find(option => option.type === rideOption);
                    this.destinationRideOption = rideOption;
                    this.destinationIcon = this.switchPopoverIcon(rideOption);
                    this.destinationOption = `${matchedOption.string[this.$i18n.locale]}`;
                }
                f7.popover.open('.marker-popover', targetElement);
            },
            switchPopoverIcon(type){
                switch(type) {
                    case 'own_scooter': {
                        return 'electric_scooter';
                    }
                    case 'own_bike': {
                        return 'pedal_bike';
                    }
                    case 'walk': {
                        return 'directions_walk';
                    }
                }
            },
            handleMarkerClick(destination) {
                this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                this.currentDestination = destination;
                this.onBookClick();
            },
            async onBookClick() {
                f7.popover.close('.marker-popover');
                
                this.showToastWait(this.$t('planning.toast.loading'));

                const directionsStart = [this.currentDestination.geoLocation.longitude, this.currentDestination.geoLocation.latitude];
                const directionsEnd = [this.currentDestination.destLongitude, this.currentDestination.destLatitude];
                let directionsData = await this.getDirectionData(directionsStart, directionsEnd, 'car');
                
                const tripData = {
                    "start_timestamp": this.getCurrentTimestamp(),
                    "location_from_latitude": this.currentDestination.geoLocation.latitude,
                    "location_from_longitude": this.currentDestination.geoLocation.longitude,
                    "location_to_latitude": this.currentDestination.destLatitude,
                    "location_to_longitude": this.currentDestination.destLongitude,
                    "user_location_latitude": this.currentDestination.geoLocation.latitude,
                    "user_location_longitude": this.currentDestination.geoLocation.longitude
                };
                
                const response = await bookingService.tripSearch(tripData);
                if (response.status === 200) {
                    this.emitter.emit('closeLastLocations', '');
                    this.closeToastWait();
                    console.log("DISTANCE: ", directionsData.distance)
                    if (directionsData.distance < this.maxDistance) {
                        this.emitter.emit('set-options-data', { destination: this.currentDestination, tripData: tripData, options: response.data.options });
                        this.emitter.emit('showRideOptions');
                        if (response.data.options.length == 0) {
                            f7.dialog.alert(this.$t('app.dialog.hint.no-offer'), this.$t('app.dialog.hint.title'));
                        }
                    } else {
                        f7.dialog.alert(this.$t('app.dialog.error.max-distance'), this.$t('app.dialog.error.title'));
                    }
                } else if (response.status === 500) {
                    this.closeToastWait();
                    this.sendHapticFeedback('REJECT', 'Error');
                    f7.dialog.alert(this.$t('app.dialog.error.bad-request'), this.$t('app.dialog.error.title'));
                } else {
                    this.closeToastWait();
                    this.sendHapticFeedback('REJECT', 'Error');
                }
            },
            async onStartClick() {
                try {
                    if (!this.destinationRideOption) return;

                    f7.popover.close('.marker-popover');

                    this.selectedStartTime = new Date().toISOString();
                    const directionsStart = [this.currentDestination.geoLocation.longitude, this.currentDestination.geoLocation.latitude];
                    const directionsEnd = [this.currentDestination.destLongitude, this.currentDestination.destLatitude];
                    let directionsData = await this.getDirectionData(directionsStart, directionsEnd, this.destinationRideOption);

                    let data = {
                        trip_mode: this.destinationRideOption,
                        state: "started",
                        from_location_latitude: this.currentDestination.geoLocation.latitude,
                        from_location_longitude: this.currentDestination.geoLocation.longitude,
                        from_description: this.currentDestination.userPlaceName,
                        to_location_latitude: this.currentDestination.destLatitude,
                        to_location_longitude: this.currentDestination.destLongitude,
                        to_description: this.currentDestination.destPlaceName,
                        start_time: this.selectedStartTime,
                        end_time: directionsData.endTime,
                        vehicle_id: ""
                    };
                    const response = await bookingService.createBooking(data);
                    if (response.status === 200) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        f7.toast.show({
                            text: this.$t('planning.sheet.ridebooking.toast.booking-trip-successful'),
                            icon: theme.ios
                            ? '<i class="f7-icons">checkmark_alt_circle</i>'
                            : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                        this.navigateToPage('/activity');
                    } else {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.toast.show({
                            text: this.$t('planning.sheet.ridebooking.toast.booking-trip-fail'),
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
            async getDirectionData(start, end, type) {
                try {
                    let url = `${this.mapboxAPI}${this.mapboxDrivingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
                    switch(type) {
                        case 'own_scooter':
                        case 'own_bike':
                            url = `${this.mapboxAPI}${this.mapboxCyclingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
                            break;
                        case 'walk':
                            url = `${this.mapboxAPI}${this.mapboxWalkingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
                            break;
                        default:
                            break;
                    }
                    const response = await axios.get(url);
                    const route = response.data.routes[0];

                    const distance = Math.ceil(route.distance);
                    const durationInSeconds = Math.ceil(route.duration);
                    const durationInMilliseconds = durationInSeconds * 1000;

                    const initialDate = new Date(this.selectedStartTime);
                    const finalDate = new Date(initialDate.getTime() + durationInMilliseconds);
                    const endTime = finalDate.toISOString();
                    const approxTimeOfArrival = formatTime(finalDate.toISOString(), this.$i18n.locale);

                    return { 
                             distance: distance, 
                             duration: durationInMilliseconds, 
                             endTime: endTime,
                             approxTimeOfArrival: approxTimeOfArrival
                           }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            showToastWait(text) {
                this.toastWaitLoading = f7.toast.create({
                    text: text,
                    destroyOnClose: true,
                    icon: `<img src="${loading}" height="48" width="48">`,
                    position: 'center'
                });
                this.toastWaitLoading.open();
            },
            closeToastWait() {
                if (!this.toastWaitLoading) return;

                this.toastWaitLoading.close();
                const toastElement = $('.toast-center');
                if (toastElement) {
                    toastElement.remove();
                }
                this.toastWaitLoading = null;
            },
            openLastDestinations() {
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                f7.sheet.open('.last-destinations-sheet');
            },
            closeLastDestinations() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close('.last-destinations-sheet');
            },
            openRideBookingCar() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.popup.open('.ride-booking-car');
            },
            closeRideBookingCar() {
                f7.popup.close('.ride-booking-car');
            },
            openRideBookingFootWay() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.popup.open('.ride-booking-foot-way');
            },
            closeRideBookingFootWay() {
                f7.popup.close('.ride-booking-foot-way');
            },
            openRideBookingPublicTransport() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.popup.open('.ride-booking-public-transport');
            },
            closeRideBookingPublicTransport() {
                f7.popup.close('.ride-booking-public-transport');
            },
            openRideBookingShared() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.popup.open('.ride-booking-shared');
            },
            closeRideBookingShared() {
                f7.popup.close('.ride-booking-shared');
            },
            openRideBookingOwnVehicle() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.popup.open('.ride-booking-own-vehicle');
            },
            closeRideBookingOwnVehicle() {
                f7.popup.close('.ride-booking-own-vehicle');
            },
            openRideBookingCar() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.popup.open('.ride-booking-car');
            },
            closeRideBookingCar() {
                f7.popup.close('.ride-booking-car');
            },
            openRideOptions() {
                f7.sheet.open('.ride-options-sheet');
            },
            closeRideOptions() {
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                f7.sheet.close('.ride-options-sheet');
            },
            getCurrentTimestamp() {
                const now = new Date();
                const localDate = new Date(now.getTime());
                const timestamp = localDate.toISOString();
                return timestamp;
            },
            navigateToPage(page) {
                f7.view.current.router.navigate(page, { history: false, clearPreviousHistory: true, ignoreCache: true });
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
            this.closeToastWait();
            this.emitter.off('showRideBookingFootWay', this.showRideBookingFootWay);
            this.emitter.off('hideRideBookingFootWay', this.hideRideBookingFootWay);
            this.emitter.off('showLastLocations', this.showLastLocations);
            this.emitter.off('hideLastLocations', this.hideLastLocations);
            this.emitter.off('showRideBookingPublicTransport', this.showRideBookingHandlerPublicTransport);
            this.emitter.off('hideRideBookingPublicTransport', this.hideRideBookingHandlerPublicTransport);
            this.emitter.off('showRideBookingShared', this.showRideBookingHandlerShared);
            this.emitter.off('hideRideBookingShared', this.hideRideBookingHandlerShared);
            this.emitter.off('showRideBookingOwnVehicle', this.showRideBookingHandlerOwnVehicle);
            this.emitter.off('hideRideBookingOwnVehicle', this.hideRideBookingHandlerOwnVehicle);
            this.emitter.off('showRideOptions', this.showRideOptions);
            this.emitter.off('hideRideOptions', this.hideRideOptions);
        },
    };
</script>
<style scoped>
    .popover-subtitle {
        font-weight: 200;
        margin-top: 0px;
        margin-bottom: 10px;
    }
    .destinationTitle {
        font-weight: 600; 
        font-size: 1.2em;
    }
    .destinationAddress {
        font-weight: 200;
    }
    .icon-container {
        position: absolute;
        padding-right: 10px;
    }
    .block-title-nomargin {
        margin-left: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    .marker-popover {
        padding: 15px;
    }
    .popover-button-wrapper {
        display: flex;
        gap: 10px;
        padding-top: 10px;
        padding-bottom: 0px;
    }
    .popover-button-wrapper .button-book,
    .popover-button-wrapper .button-start {
        flex: 1;
    }
</style>