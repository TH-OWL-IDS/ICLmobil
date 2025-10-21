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
              style="height: 90vh" 
              backdrop
              swipe-to-close
              :close-by-backdrop-click="false" 
              :close-by-outside-click="false" 
              class="ride-options-sheet">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar">
            <div class="left sheet-title">
                {{ title }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-page-content>
            <f7-block class="no-padding-top no-margin-top">
                <div class="list dividers-ios list-strong-ios no-margin-top">
                    <ul>
                        <li>
                            <div class="item-content item-input">
                                <div class="item-inner" @click="openDatePicker">
                                    <div class="item-title item-label">{{ this.$t('planning.sheet.rideoptions.date') }}</div>
                                    <div class="item-input-wrap">
                                        <input 
                                            type="text" 
                                            :placeholder="this.$t('planning.sheet.rideoptions.pickdate')" 
                                            readonly="readonly" 
                                            id="datePicker" />
                                    </div>
                                </div>
                                <div class="item-after">
                                    <i @click="openDatePicker" class="icon f7-icons">pencil</i>
                                </div>
                            </div>
                        </li>
                        <li>
                            <div class="item-content item-input">
                                <div class="item-inner" @click="openTimePicker">
                                    <div class="item-title item-label">{{ this.$t('planning.sheet.rideoptions.time') }}</div>
                                    <div class="item-input-wrap">
                                        <input
                                            id="timerPicker"
                                            type="text"
                                            :placeholder="this.$t('planning.sheet.rideoptions.picktime')"
                                            readonly="readonly"
                                        />
                                    </div>
                                </div>
                                <div class="item-after">
                                    <i @click="openTimePicker" class="icon f7-icons">pencil</i>
                                </div>
                            </div>
                        </li>
                        <li>
                            <div class="item-content item-input">
                                <div class="item-inner" @click="openLastDestinations">
                                    <div class="item-title item-label">{{ this.$t('planning.sheet.rideoptions.destination') }}</div>
                                    <div class="item-input-wrap">
                                        <input type="text" readonly="readonly" :placeholder="this.$t('planning.sheet.rideoptions.pickdestination')" name="destination" :value="destination.destPlaceName" />
                                    </div>
                                </div>
                                <div class="item-after">
                                    <i @click="openLastDestinations" class="icon f7-icons">pencil</i>
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </f7-block>

            <f7-block>
                <f7-block-title medium>{{ this.$t('planning.sheet.rideoptions.youroptionstitle') }}</f7-block-title>
                <f7-segmented strong ref="segmentedControl">
                    <!-- <f7-button
                    :class="{ 'button-active': activeOption === 0 }"
                    @click="toggleFilter(0)">
                        <span class="icon_scooter">
                            <i class="material-icons">{{ iconScooter }}</i>
                        </span>
                    </f7-button> -->
                    <f7-button
                    :class="{ 'button-active': activeOption === 0 }"
                    @click="toggleFilter(0)">
                    <span class="icon_bike">
                        <i class="material-icons">bike_scooter</i>
                    </span>
                    </f7-button>
                    <f7-button
                    :class="{ 'button-active': activeOption === 1 }"
                    @click="toggleFilter(1)"
                    :disabled="isDisabled('bus')">
                        <span class="icon_bus">
                            <i class="material-icons">{{ iconBus }}</i>
                        </span>
                    </f7-button>
                    <f7-button
                    :class="{ 'button-active': activeOption === 2 }" 
                    @click="toggleFilter(2)">
                        <span class="icon_car">
                            <i class="material-icons">{{ iconCar }}</i>
                        </span>
                    </f7-button>
                    <f7-button
                    :class="{ 'button-active': activeOption === 3 }" 
                    @click="toggleFilter(3)"
                    :disabled="isDisabled('walk')">
                        <span class="icon_walk">
                            <i class="material-icons">{{ iconWalk }}</i>
                        </span>
                    </f7-button>
                </f7-segmented>

                <f7-list dividers-ios strong-ios>
                    <f7-list-item 
                        v-for="option in filteredRideOptions" 
                        link="#"
                        @click="openRideBooking(option.optionID)" 
                        :key="option.optionID"
                        :title="option.rideOption" 
                        :footer="`${option.rideDate} - ${option.rideTimestamp}`">
                        <template #media>
                            <i class="material-icons">{{ option.rideIcon }}</i>
                        </template>
                    </f7-list-item>
                    <f7-list-button v-if="activeOption === 0" @click="useOwnVehicle('scooter')" :title="this.$t('planning.sheet.rideoptions.button.use-own-scooter')" color="blue"></f7-list-button>
                    <f7-list-button v-if="activeOption === 0" @click="useOwnVehicle('bike')" :title="this.$t('planning.sheet.rideoptions.button.use-own-bike')" color="blue"></f7-list-button>
                    <f7-list-button v-if="activeOption === 2 && !pooling_is_linked" @click="navigateToPage('/carPoolSetup')" :title="this.$t('planning.sheet.ridebooking.button.linkpooling')" color="blue"></f7-list-button>
                    <f7-list-button v-if="activeOption === 2 && pooling_is_linked" @click="useOwnVehicle('car')" :title="this.$t('planning.sheet.rideoptions.button.offercarpooling')" color="blue"></f7-list-button>
                </f7-list>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page-content>
    </f7-sheet>
</template>
<script>
    import { f7, f7Sheet, f7Button, f7ListButton, f7Segmented, f7ready } from 'framework7-vue';
    import $ from "dom7";
    import axios from 'axios';

    import { formatTime } from '@/js/utilities/timeFormatter';
    import { formatDate } from '@/js/utilities/dateFormatter';

    import loading from "../assets/icons/loading.gif";

    import bookingService from '../services/bookingService';

    export default {
        props: {
            title: String
        },
        components: {
            f7Sheet,
            f7Button,
            f7Segmented,
            f7ListButton
        },
        data() {
            return {
                accessToken: this.$store.getters.getMapboxToken,
                mapboxAPI: this.$store.getters.getMapboxApi,
                mapboxCyclingURI: this.$store.getters.getMapboxCyclingURI,
                mapboxDrivingURI: this.$store.getters.getMapboxDrivingURI,
                poolingRideOfferURL: this.$store.getters.getPoolingRideOffer,
                destination: {},
                tripData: {},
                options: {},
                selectedTime: null,
                selectedDate: null,
                selectedStartTime: null,
                debounceReloadTime: 500,
                debounceTimeout: null,
                activeOption: 0,
                calendarInstance: null,
                timerPicker: null,
                datePicker: null,
                iconScooter: 'electric_scooter',
                iconBike: 'pedal_bike',
                iconBus: 'directions_bus',
                iconCar: 'directions_car',
                iconWalk: 'directions_walk',
                allowedTypes: ['scooter', 'bike', 'bus', 'car', 'walk'],
                locale: this.$store.getters.getAppLocaleString,
                toastWait: null
            };
        },
        computed: {
            inAppBrowser() {
                return this.$store.getters.getPluginInAppBrowser;
            },
            pooling_is_linked() {
                return this.$store.getters.getPoolingIsLinked;
            },
            rideOptions: {
                get() {
                    return this.$store.getters.getRideOptions(this.$i18n.locale);
                },
                set(v) {
                    this.$store.dispatch('setRideOptions', { rideOptions: v });
                }
            },
            rideOptionsUnformated() {
                return this.$store.getters.getRideOptionsUnformated;
            },
            filteredRideOptions() {
                if (this.activeOption === null) return this.rideOptions;

                const types = [
                    ["bike", "scooter"],
                    ["bus"],
                    ["car"],
                    ["walk"]
                ];
                const selectedTypes = types[this.activeOption];
                return this.rideOptions.filter(option => selectedTypes.includes(option.vehicleType) && option.valid);            
            },
            appLanguage() {
                return this.$store.getters.getAppLanguage;
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        mounted() {
            f7ready(async () => {
                this.emitter.on('set-options-data', (data) => {
                    this.destination = data.destination;
                    this.tripData = data.tripData;
                    this.options = data.options;
                    this.rideOptions = this.options;
                });
            });
        },
        methods: {
            init() {
                console.log("SHEET OPENED RIDE OPTIONS")
                console.log("DESTINATION: ", this.destination)
                console.log("TRIP DATA: ", this.tripData)
                console.log("RIDE OPTIONS: ", this.rideOptions)
                this.updateHighlight();
                this.initDatePicker();
                this.initTimePicker(this.appLanguage, this.$t('planning.sheet.rideoptions.time-suffix'));
                this.resetFilter();
            },
            onClose() {
                console.log("SHEET RIDE OPTIONS CLOSED")
                this.resetDateTime();
            },
            async reloadRideOptions() {
                const newTripData = 
                {
                    "start_timestamp": this.selectedStartTime,
                    "location_from_latitude": this.destination.geoLocation.latitude,
                    "location_from_longitude": this.destination.geoLocation.longitude,
                    "location_to_latitude": this.destination.destLatitude,
                    "location_to_longitude": this.destination.destLongitude,
                    "user_location_latitude": this.destination.geoLocation.latitude,
                    "user_location_longitude": this.destination.geoLocation.longitude
                }
                console.log("NEW TRIP: ", newTripData)
                const response = await bookingService.tripSearch(newTripData);
                if (response.status === 200) {
                    this.rideOptions = response.data.options;
                }
            },
            closeTimePicker() {
                if (this.timerPicker && this.timerPicker.opened) { this.timerPicker.close(); }
            },
            closeDatePicker() {
                if (this.datePicker && this.datePicker.opened) { this.datePicker.close(); }
            },
            openDatePicker() {
                this.closeTimePicker();
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                this.datePicker.open();
            },
            openTimePicker() {
                this.closeDatePicker();
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                this.timerPicker.open();
            },
            initTimePicker(language, suffix) {
                const today = new Date();

                // We initilize the time to now + 10 minutes
                today.setMinutes(today.getMinutes() + 10);

                // Make sure hours and minutes always show a trailing zero 
                const formattedHours = String(today.getHours()).padStart(2, '0');
                const formattedMinutes = String(today.getMinutes()).padStart(2, '0');

                this.timerPicker = f7.picker.create({
                    inputEl: '#timerPicker',
                    sheetSwipeToClose: false,
                    rotateEffect: true,
                    openIn: 'sheet',
                    toolbar: true,
                    toolbarCloseText: this.$t('planning.sheet.rideoptions.picker.close'),
                    cols: [
                        {
                            textAlign: 'left',
                            values: Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0')).join(' ').split(' '),
                        },
                        {
                            divider: true,
                            content: ':',
                        },
                        {
                            values: Array.from({ length: 60 }, (_, i) => String(i).padStart(2, '0')).join(' ').split(' '),
                        },
                    ],
                    value: [ formattedHours, formattedMinutes ],
                    formatValue: function (values, displayValues) {
                        const hours = parseInt(displayValues[0], 10);
                        const minutes = displayValues[1];
                        let displayHours = hours;
                        if (language != 'de') {
                            suffix = hours >= 12 ? 'PM' : 'AM';
                            displayHours = hours % 12 || 12;
                        }
                        return `${String(displayHours).padStart(2, '0')}:${minutes} ${suffix}`;
                    },
                    on: {
                        change: (picker, value, displayValue) => {
                            const selectedHours = parseInt(value[0], 10);
                            const selectedMinutes = parseInt(value[1], 10);
                            
                            const selectedDate = new Date(this.selectedDate);
                            const selectedTime = selectedDate;
                            selectedTime.setHours(selectedHours);
                            selectedTime.setMinutes(selectedMinutes);

                            const currentTime = new Date();

                            const isToday = selectedDate.toLocaleDateString() === today.toLocaleDateString();

                            if (isToday && selectedTime < currentTime) {
                                picker.setValue([formattedHours, formattedMinutes], 0);
                                this.handleTimeChange([formattedHours, formattedMinutes]);
                            } else {
                                this.handleTimeChange(displayValue);
                            }
                        },
                        close: () => {
                            this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                        }
                    }
                });
            },
            initDatePicker() {
                const today = this.getToday();
                const thisYear = today.getFullYear();
                const lastYear = thisYear -1;
                const nextYear = today.getFullYear() + 1;

                this.datePicker = f7.calendar.create({
                    inputEl: '#datePicker',
                    dateFormat: 'dd.mm.yyyy',
                    locale: this.$store.getters.getAppLocaleString,
                    value: [new Date()],
                    yearPickerMin: lastYear,
                    yearPickerMax: nextYear,
                    openIn: 'customModal',
                    minDate: today,
                    closeOnSelect: true,
                    yearPicker: false,
                    monthPicker: false,
                    maxDate: new Date(nextYear, 11, 31),
                    on: {
                        change: (calendar, value) => {
                            const selectedDate = new Date(value[0]);
                            if (selectedDate < today) {
                                this.handleDateChange(today);
                                calendar.setValue([today]);
                            } else {
                                this.handleDateChange(value);
                            }
                        },
                        close: () => {
                            this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                        }
                    }
                });
            },
            getToday() {
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                return today;
            },
            isDisabled(option) {
                const existingTypes = this.rideOptions.map(option => option.vehicleType);
                return !existingTypes.includes(option);
            },
            toggleFilter(option) {
                this.activeOption = this.activeOption === option ? null : option;
                this.sendHapticFeedback("SEGMENT_TICK", "SelectionChanged");
                this.updateHighlight();
            },
            resetFilter() {
                // if (!this.isDisabled('scooter')) { this.activeOption = 0; }
                if (!this.isDisabled('bike')) { this.activeOption = 0; }
                else if (!this.isDisabled('bus')) { this.activeOption = 1; }
                else if (!this.isDisabled('car')) { this.activeOption = 2; }
                else if (!this.isDisabled('walk')) { this.activeOption = 3; }
                this.updateHighlight();
            },
            resetDateTime() {
                this.datePicker.destroy();
                this.timerPicker.destroy();
                this.selectedDate = null;
                this.selectedTime = null;
                this.selectedStartTime = null;
            },
            updateHighlight() {
                const highlight = this.$refs.segmentedControl.$el.querySelector('.segmented-highlight');
                if (highlight) {
                    highlight.style.display = this.activeOption === null ? 'none' : 'block';
                }
                this.closeDatePicker();
                this.closeTimePicker();
            },
            initializeCalendar(calendar) {
                this.calendarInstance = calendar;
            },
            handleDateChange(selectedDate) {
                this.selectedDate = selectedDate;
                if (this.datePicker) {
                    this.datePicker.close();
                }
                this.formatNewStarttime();
                if (!this.destination.destLatitude ||
                    !this.destination.destLongitude
                ) return;
                this.debounceReload();
            },
            handleTimeChange(selectedTime) {
                this.selectedTime = selectedTime;
                this.formatNewStarttime();
                if (!this.destination.destLatitude ||
                    !this.destination.destLongitude
                ) return;
                this.debounceReload();
            },
            formatNewStarttime() {
                if (this.selectedDate && this.selectedTime) {
                    const date = new Date(this.selectedDate);
                    const hours = parseInt(this.selectedTime[0], 10);
                    const minutes = parseInt(this.selectedTime[1], 10);
                    date.setHours(hours);
                    date.setMinutes(minutes);
                    this.selectedStartTime = date.toISOString();
                }
            },
            debounceReload() {
                if (!this.selectedStartTime) return;

                if (this.debounceTimeout) {
                    clearTimeout(this.debounceTimeout);
                }
                this.debounceTimeout = setTimeout(() => {
                    this.reloadRideOptions();
                }, this.debounceReloadTime);
            },
            openSheet() {
                f7.sheet.open('.ride-options-sheet');
            },
            closeSheet() {
                this.closeDatePicker();
                this.closeTimePicker();
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close('.ride-options-sheet');
            },
            openRideBooking(selectedRideID) {
                this.closeDatePicker();
                this.closeTimePicker();
                const foundOption = this.rideOptions.find(options => options.optionID === selectedRideID);
                const foundOptionUnformated = this.rideOptionsUnformated.find(options => options.optionID === selectedRideID);
                
                switch(foundOption.vehicleType) {
                    case "bus":
                        this.emitter.emit('set-ride-booking-public-transport', { selectedRideOption: foundOption, selectedRideOptionUnformated: foundOptionUnformated, destination: this.destination } );
                        this.emitter.emit('showRideBookingPublicTransport', '');
                        break;
                    case "scooter":
                    case "bike":
                        this.emitter.emit('set-ride-booking-shared', { selectedRideOption: foundOption, selectedRideOptionUnformated: foundOptionUnformated, destination: this.destination } );
                        this.emitter.emit('showRideBookingShared', '');
                        break;
                    case "car":
                        this.emitter.emit('set-ride-booking-car', { selectedRideOption: foundOption, selectedRideOptionUnformated: foundOptionUnformated, destination: this.destination } );
                        this.emitter.emit('showRideBookingCar', '');
                        break;
                    case "walk":
                        this.emitter.emit('set-ride-booking-foot-way', { selectedRideOption: foundOption, selectedRideOptionUnformated: foundOptionUnformated, destination: this.destination } );
                        this.emitter.emit('showRideBookingFootWay', '');
                        break;
                    default:
                        break;
                }
            },
            async useOwnVehicle(vehicleType) {
                this.closeDatePicker();
                this.closeTimePicker();
                this.showToastWait(this.$t('planning.sheet.rideoptions.toast.wait'));
                let customSelectedRide = null;

                const directionsStart = [this.tripData.user_location_longitude, this.tripData.user_location_latitude];
                const directionsEnd = [this.destination.destLongitude, this.destination.destLatitude];
                let directionsData = null;
                switch(vehicleType) {
                    case "scooter":
                        directionsData = await this.getDirectionData(directionsStart, directionsEnd, 'scooter');
                        customSelectedRide = {
                            optionType: 'own_scooter',
                            rideDate: formatDate(this.selectedStartTime, this.$i18n.locale),
                            rideTimestamp: formatTime(this.selectedStartTime, this.$i18n.locale),
                            start_time: this.selectedStartTime,
                            end_time: directionsData.endTime,
                            approxTimeOfArrival: directionsData.approxTimeOfArrival,
                            vehicleType: 'scooter',
                            vehicleId: null
                        }
                        this.emitter.emit('set-ride-booking-own-vehicle', { selectedRideOption: customSelectedRide, destination: this.destination } );
                        this.emitter.emit('showRideBookingOwnVehicle', '');
                        this.closeToastWait();
                        break;
                    case "bike":
                        directionsData = await this.getDirectionData(directionsStart, directionsEnd, 'bike');
                        customSelectedRide = {
                            optionType: 'own_bike',
                            rideDate: formatDate(this.selectedStartTime, this.$i18n.locale),
                            rideTimestamp: formatTime(this.selectedStartTime, this.$i18n.locale),
                            start_time: this.selectedStartTime,
                            end_time: directionsData.endTime,
                            approxTimeOfArrival: directionsData.approxTimeOfArrival,
                            vehicleType: 'bike',
                            vehicleId: null
                        }
                        this.emitter.emit('set-ride-booking-own-vehicle', { selectedRideOption: customSelectedRide, destination: this.destination } );
                        this.emitter.emit('showRideBookingOwnVehicle', '');
                        this.closeToastWait();
                        break;
                    case "car":
                        const rideOfferURL = this.poolingRideOfferURL.replace('rideoffer/', '');
                        if (this.inAppBrowser) {
                            this.inAppBrowser.open(rideOfferURL, '_system');
                        }
                        this.closeToastWait();
                        break;
                    default:
                        this.closeToastWait();
                        break;
                }
            },
            async getDirectionData(start, end, type) {
                try {
                    let url = `${this.mapboxAPI}${this.mapboxDrivingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
                    switch(type) {
                        case 'scooter':
                        case 'bike':
                            url = `${this.mapboxAPI}${this.mapboxCyclingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;
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
                    this.closeToastWait();
                    this.sendHapticFeedback('REJECT', 'Error');
                    f7.dialog.alert(this.$t('app.dialog.error.bad-booking'), this.$t('app.dialog.error.title'));
                }
            },
            openLastDestinations() {
                this.closeDatePicker();
                this.closeTimePicker();
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                f7.sheet.close('.ride-options-sheet');
                this.emitter.emit('showLastLocations', '');
            },
            showToastWait(text) {
                this.toastWait = f7.toast.create({
                    text: text,
                    destroyOnClose: true,
                    icon: `<img src="${loading}" height="48" width="48">`,
                    position: 'center'
                });
                this.toastWait.open();
            },
            closeToastWait() {
                if (!this.toastWait) return;

                this.toastWait.close();
                const toastElement = $('.toast-center');
                if (toastElement) {
                    toastElement.remove();
                }
                this.toastWait = null;
            },
            navigateToPage(page) {
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                this.closeSheet();
                f7.view.current.router.navigate(page, { history: true, clearPreviousHistory: false, ignoreCache: true });
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
            this.emitter.off('set-options-data');
        }
    };
</script>