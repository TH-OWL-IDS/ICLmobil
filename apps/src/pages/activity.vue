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
      
        <NavBar ref="navBar" :title="title" :large="true" :showSearch="false" :showIcons="true"/>
        
        <f7-page :page-content="true"
                  ptr 
                  :ptr-mousewheel="true"
                  @ptr:refresh="onRefresh">
            
            <!-- NEXT RIDES -->
            <f7-block-title medium>{{ this.$t('activity.nextrides.title') }}</f7-block-title>
            <div v-if="nextRides.length > 0" data-cy="activity-nextrides-lst" class="list inset list-dividers list-strong media-list chevron-center" style="--f7-list-strong-bg-color: #96D35F; --f7-list-chevron-icon-color: #fff">
                <ul>
                    <li v-for="ride in nextRides" :key="ride.id">
                        <div v-if="ride.state === 'canceled'" class="item-content canceled-item">
                            <div class="item-media">
                                <span class="icon_white_large">
                                    <i class="material-icons" style="font-size: 48px">{{ ride.rideIcon }}</i>
                                </span>
                            </div>
                            <div class="item-inner">
                                <div class="item-title-row">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.nextrides.when') }}</div>
                                </div>
                                <div class="item-subtitle" style="--f7-list-item-subtitle-text-color: #fff">{{ ride.rideDate }} - {{ ride.rideTime }}</div>
                                <div class="item-title-row" style="padding-top: 10px">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.nextrides.where') }}</div>
                                </div>
                                <div class="item-text" style="--f7-list-item-text-text-color: #fff">{{ ride.rideDestination }}</div>
                            </div>
                            <div class="canceled-stamp-container">
                                <img src="../assets/backgrounds/canceled.png" alt="CANCELED" class="canceled-stamp" />
                            </div>
                        </div>
                        
                        <a v-else class="item-link item-content" @click="openNextRide(ride)">
                            <div class="item-title-end"><span class="badge color-orange">{{ this.$t('activity.nextrides.badge') }}</span></div>
                            <div class="item-media">
                                <span class="icon_white_large">
                                    <i class="material-icons" style="font-size: 48px">{{ ride.rideIcon }}</i>
                                </span>
                            </div>
                            <div class="item-inner">
                                <div class="item-title-row">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.nextrides.when') }}</div>
                                </div>
                                <div class="item-subtitle" style="--f7-list-item-subtitle-text-color: #fff">{{ ride.rideDate }} - {{ ride.rideTime }}</div>
                                <div class="item-title-row" style="padding-top: 10px">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.nextrides.where') }}</div>
                                </div>
                                <div class="item-text" style="--f7-list-item-text-text-color: #fff">{{ ride.rideDestination }}</div>
                            </div>
                        </a>
                    </li>
                </ul>
            </div>
            <div v-else class="no-next-rides-background">
                <div class="no-next-rides-text text-align-center block-title block-title-medium">
                    {{ this.$t('activity.nextrides.no-next-rides-found') }}
                </div>
                <div class="no-next-rides-text text-align-center">
                    <f7-button @click="bookRide" data-cy="activity-nonextrides-btn" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:map_pin_ellipse" md="material:explore"></f7-icon>&nbsp; {{ this.$t('activity.link.book-now') }}</f7-button>
                </div>
            </div>

            <!-- STARTED RIDES -->
            <f7-block-title medium v-if="startedRides.length > 0">{{ this.$t('activity.startedrides.title') }}</f7-block-title>
            <div v-if="startedRides.length > 0" data-cy="activity-startedrides-lst" class="list inset list-dividers list-strong media-list chevron-center" style="--f7-list-strong-bg-color: #96D35F; --f7-list-chevron-icon-color: #fff">
                <ul>
                    <li v-for="ride in startedRides" :key="ride.id">
                        <a class="started-item item-link item-content" @click="openStartedRide(ride)">
                            <div class="item-title-end"><span class="badge color-blue">{{ this.$t('activity.startedrides.badge') }}</span></div>
                            <div class="item-media">
                                <span class="icon_white_large">
                                    <i class="material-icons" style="font-size: 48px">{{ ride.rideIcon }}</i>
                                </span>
                            </div>
                            <div class="item-inner">
                                <div class="item-title-row">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.startedrides.when') }}</div>
                                </div>
                                <div class="item-subtitle" style="--f7-list-item-subtitle-text-color: #fff">{{ ride.rideDate }} - {{ ride.rideTime }}</div>
                                <div class="item-title-row" style="padding-top: 10px">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.startedrides.where') }}</div>
                                </div>
                                <div class="item-text" style="--f7-list-item-text-text-color: #fff">{{ ride.rideDestination }}</div>
                            </div>
                        </a>
                    </li>
                </ul>
            </div>

            <!-- PREVIOUS RIDES -->
            <f7-block-title medium>{{ this.$t('activity.previousrides.title') }}</f7-block-title>
            <div v-if="previousRides.length > 0" data-cy="activity-previousrides-lst" class="list inset list-dividers list-strong media-list chevron-center" style="--f7-list-strong-bg-color: #96D35F; --f7-list-chevron-icon-color: #fff">
                <ul>
                    <li v-for="ride in previousRides" :key="ride.id" class="swipeout" @swipeout:delete="deleteTrip(ride.id)">
                        <div v-if="ride.state === 'canceled'" class="item-content swipeout-content canceled-item">
                            <div class="item-media">
                                <span class="icon_white_large">
                                    <i class="material-icons" style="font-size: 48px">{{ ride.rideIcon }}</i>
                                </span>
                            </div>
                            <div class="item-inner">
                                <div class="item-title-row">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.previousrides.when') }}</div>
                                </div>
                                <div class="item-subtitle" style="--f7-list-item-subtitle-text-color: #fff">{{ ride.rideDate }} - {{ ride.rideTime }}</div>
                                <div class="item-title-row" style="padding-top: 10px">
                                    <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.previousrides.where') }}</div>
                                </div>
                                <div class="item-text" style="--f7-list-item-text-text-color: #fff">{{ ride.rideDestination }}</div>
                            </div>
                            <div class="canceled-stamp-container">
                                <img src="../assets/backgrounds/canceled.png" alt="CANCELED" class="canceled-stamp" />
                            </div>
                        </div>
                        <div v-else-if="ride.state !== 'started'" class="swipeout-content">
                            <a class="item-link item-content" @click="openPreviousRide(ride)">
                                <div class="item-title-end"><span class="badge color-green">{{ this.$t('activity.previousrides.badge') }}</span></div>
                                <div class="item-media">
                                    <span class="icon_white_large">
                                        <i class="material-icons" style="font-size: 48px">{{ ride.rideIcon }}</i>
                                    </span>
                                </div>
                                <div class="item-inner">
                                    <div class="item-title-row">
                                        <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.previousrides.when') }}</div>
                                    </div>
                                    <div class="item-subtitle" style="--f7-list-item-subtitle-text-color: #fff">{{ ride.rideDate }} - {{ ride.rideTime }}</div>
                                    <div class="item-title-row" style="padding-top: 10px">
                                        <div class="item-title" style="--f7-list-item-title-text-color: #fff">{{ this.$t('activity.previousrides.where') }}</div>
                                    </div>
                                    <div class="item-text" style="--f7-list-item-text-text-color: #fff">{{ ride.rideDestination }}</div>
                                </div>
                            </a>
                        </div>
                        <div class="swipeout-actions-right">
                            <a href="#" :data-confirm="this.$t('activity.sheet.previousride.dialog.confirmDeleteText')" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" class="swipeout-delete swipeout-overswipe">Delete</a>
                        </div>
                    </li>
                </ul>
            </div>
            <div v-else class="no-previous-rides-background">
                <div class="no-previous-rides-text text-align-center block-title block-title-medium">
                    {{ this.$t('activity.previousrides.no-last-rides-found') }}
                </div>
                <div class="no-previous-rides-text text-align-center">
                    <f7-button @click="bookRide" data-cy="activity-nopreviousrides-btn" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:map_pin_ellipse" md="material:explore"></f7-icon>&nbsp; {{ this.$t('activity.link.book-now') }}</f7-button>
                </div>
            </div>
            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" :tabActive="tabActive"/>

        <NextRide/>
        <StartedRide/>
        <PreviousRide/>
        <RideFeedback/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link, theme } from 'framework7-vue';

  import bookingService from '@/services/bookingService';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';
  import NextRide from '../components/next_ride.vue';
  import StartedRide from '../components/started_ride.vue';
  import PreviousRide from '../components/previous_ride.vue';
  import RideFeedback from '../components/feedback.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Tabs,
        f7Tab,
        f7Link,
        NavBar,
        ToolBar,
        NextRide,
        StartedRide,
        PreviousRide,
        RideFeedback
    },
    data() {
        return {
            title: this.$t('activity.title'),
            tabActive: 3,
     };
    },
    computed: {
        nextRides() {
            const next = this.$store.getters.getNextRides(this.$i18n.locale);
            return this.$store.getters.getNextRides(this.$i18n.locale);
        },
        startedRides() {
            const started = this.$store.getters.getStartedRides(this.$i18n.locale);
            return this.$store.getters.getStartedRides(this.$i18n.locale);
        },
        previousRides() {
            const previous = this.$store.getters.getPreviousRides(this.$i18n.locale);
            return this.$store.getters.getPreviousRides(this.$i18n.locale);
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    async created() {
        this.emitter.on('refresh-booking-list', async () => {
            await this.loadRides();
        });
        this.emitter.on('open-started-ride', (ride) => {
            this.openStartedRide(ride);
        });
        await this.loadRides();
    },
    methods: {
        onRefresh: async function (done) {
            await this.loadRides();
            done();
        },
        bookRide() {
            f7.view.current.router.navigate('/planning', { history: false, clearPreviousHistory: true, ignoreCache: true, animate: false });
        },
        async loadRides() {
            try {
                console.log("REFRESH BOOKING LIST...")
                const response = await bookingService.getBookings();
                if (response.status === 200) {
                    this.$store.dispatch('setNextRides', { rides: response.data.nextRides });
                    this.$store.dispatch('setPreviousRides', { rides: response.data.previousRides });
                } else if (response.status === 401) {
                    f7.dialog.alert(this.$t('app.dialog.error.not-authorized'), this.$t('app.dialog.error.title'));
                }
            } catch (err) {
                console.log(err)
            }
        },
        async deleteTrip(id) {
            try {
                const response = await bookingService.deleteBooking(id);
                if (response.msg) {
                    this.sendHapticFeedback('CONFIRM', 'Success');
                    f7.toast.show({
                        text: this.$t('activity.toast.delete-trip-successful'),
                        icon: theme.ios
                            ? '<i class="f7-icons">checkmark_alt_circle</i>'
                            : '<i class="material-icons">check_circle</i>',
                        position: 'center',
                        closeTimeout: 2000,
                        destroyOnClose: true
                    });
                } else if (response.error) {
                    this.sendHapticFeedback('REJECT', 'Error');
                    f7.toast.show({
                        text: this.$t('activity.toast.delete-trip-fail'),
                        icon: theme.ios
                            ? '<i class="f7-icons">exclamationmark_triangle</i>'
                            : '<i class="material-icons">error</i>',
                        position: 'center',
                        closeTimeout: 2000,
                        destroyOnClose: true
                    });
                }
                await this.loadRides();
            } catch(err) {
                console.log("ERROR: ", err)
            }
        },
        openNextRide(selectedRide) {
            this.emitter.emit('set-next-ride-data', selectedRide);
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            f7.sheet.open('.nextRide');
        },
        openStartedRide(selectedRide) {
            this.emitter.emit('set-started-ride-data', selectedRide);
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            f7.sheet.open('.startedRide');
        },
        openPreviousRide(selectedRide) {
            this.emitter.emit('set-previous-ride-data', selectedRide);
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            f7.sheet.open('.previousRide');
        },
        sendHapticFeedback(androidType, iosType) {
            if (this.hapticFeedback) {
                this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                    console.error("HAPTIC ERROR: ", error);
                });
            }
        }
    }
  };
</script>
<style scoped>
.item-title-end {
    display: flex;
    justify-content: right;
    position: absolute;
    right: 0;
    top: 0;
    padding: 10px 10px 10px 10px;
}
.canceled-item {
    background-color: #ddd;
    position: relative;
}
.canceled-stamp-container {
    display: flex;
    justify-content: center;
    width: 100%;
    position: absolute;
    top: 50%;
    left: 0px;
    transform: translateY(-50%);
}
.canceled-stamp {
    width: 80%;
    opacity: 0.3;
}
</style>