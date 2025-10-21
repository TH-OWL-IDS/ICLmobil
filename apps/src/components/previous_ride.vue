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
              :close-by-backdrop-click="true" 
              :close-by-outside-click="true" 
              class="previousRide">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar">
            <div class="left sheet-title">
                {{ title }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet" data-cy="previousride-close-btn">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-page-content>
            <f7-block class="no-padding-top no-margin-top">
                <div class="grid grid-cols-1">
                    <div style="text-align: center"><img :src="titleBanner" style="max-width: 70%; height: auto;"/></div>
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
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.previousride.when') }}</td>
                                <td>{{ localRide.rideDate }} - {{ localRide.rideTime }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.previousride.ridestart') }}</td>
                                <td><div v-html="localRide.rideStart"></div></td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.previousride.ridedestination') }}</td>
                                <td><div v-html="localRide.rideDestination"></div></td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.previousride.departure') }}</td>
                                <td>{{ this.$t('activity.sheet.nextride.approximate') }} {{ localRide.rideTime }}</td>
                            </tr>
                            <tr>
                                <td class="label-cell table-text-bold">{{ this.$t('activity.sheet.previousride.arrival') }}</td>
                                <td>{{ this.$t('activity.sheet.previousride.approximate') }} {{ localRide.approxTimeOfArrival }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </f7-block>

            <f7-block>
                <div v-if="localRide.type != 'rriveUse'">
                    <f7-button href="#" @click="cancelRide" data-cy="previousride-cancel-btn" fill large style="background-color: #FF0000 !important; --f7-button-large-text-transform: none">
                        <div v-if="localRide.type === 'walk'">{{ this.$t('activity.sheet.previousride.button.walknottaken') }}</div>
                        <div v-else>{{ this.$t('activity.sheet.previousride.button.ridenottaken') }}</div>
                    </f7-button>
                </div>

                <div v-if="localRide.type == 'rriveUse'">
                    <f7-button href="#" @click="takeMeToCarPool" data-cy="previousride-gotocarpool-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">{{ this.$t('activity.sheet.previousride.button.takemetopool') }}</f7-button>
                </div>
                
                <div class="button-wrapper">
                    <f7-button href="#" @click="leaveFeedback" data-cy="previousride-feedback-btn" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none"><i class="icon f7-icons" style="font-size: 22px">hand_thumbsup_fill</i>&nbsp;{{ this.$t('activity.sheet.previousride.button.ridefeedback') }}</f7-button>
                </div>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page-content>
    </f7-sheet>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';

    import bookingService from '../services/bookingService';

    import scooter from "../assets/placeholder/images/scooter.png";
    import bike from "../assets/placeholder/images/bike.png";
    import bus from "../assets/placeholder/images/bus.png";
    import car from "../assets/placeholder/images/car.png";
    import walk from "../assets/placeholder/images/walk.png";
  
    export default {
        components: {
            f7,
            f7ready,
            f7Page,
            f7Block,
            f7Link
        },
        data() {
            return {
                title: this.$t('activity.sheet.previousride.title'),
                titleBanner: scooter,
                localRide: {},
                poolingPreviousPassengerURL: this.$store.getters.getPoolingPreviousPassenger,
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
            this.emitter.on('set-previous-ride-data', (ride) => {
                this.localRide = { ...ride };
                this.changeBanner(this.localRide.rideIcon);
            });
        },
        methods: {
            init() {
                console.log("SHEET PREVIOUS RIDE OPENED")
            },
            onClose() {
                console.log("SHEET CLOSING")
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
            takeMeToCarPool() {
                try {
                    this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                    if (this.localRide.provider_id) {
                        const url = this.poolingPreviousPassengerURL + this.localRide.provider_id;
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
            async cancelRide() {
                try {
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
                        f7.toast.show({
                            text: this.$t('app.dialog.success.ride-cancel'),
                            icon: theme.ios
                            ? '<i class="f7-icons">checkmark_alt_circle</i>'
                            : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                        this.emitter.emit('refresh-booking-list', '');
                        this.closeSheet();
                    } else if (response.error) {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.toast.show({
                            text: this.$t('app.dialog.error.ride-cancel'),
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
            leaveFeedback() {
                this.closeSheet();
                this.emitter.emit('set-ride-feedback-data', this.localRide);
                this.emitter.emit('open-feedback');
            },
            closeSheet() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close('.previousRide');
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
            this.emitter.off('set-previous-ride-data');
        },
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
    .button-wrapper {
        padding-top: 20px;
        padding-bottom: 20px;
    }
</style>