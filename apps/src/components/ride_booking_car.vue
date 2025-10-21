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
            swipe-handler=".swipe-handler" 
            swipe-to-close 
            style="height: 90vh" 
            :close-by-backdrop-click="false" 
            :close-by-outside-click="false" 
            class="ride-booking-car">
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

    <f7-page-content class="sheet-content-extra-padding">
      <f7-block>
        <div class="grid grid-cols-1">
          <div style="text-align: center"><img :src="placeholder" style="max-width: 80%; height: auto;"/></div>
        </div>
        <div class="data-table">
          <table>
            <tbody>
              <tr>
                <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.ridedestination') }}</td>
                <td>{{ destination.destPlaceName }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.when') }}</td>
                  <td>{{ selectedRideOption.rideDate }} - {{ selectedRideOption.rideTimestamp }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.arrival') }}</td>
                  <td>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ selectedRideOption.approxTimeOfArrival }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.distance') }}</td>
                  <td>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ selectedRideOption.distanceM }} {{ this.$t('planning.sheet.ridebooking.distanceunit') }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.distance') }}</td>
                  <td>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ distanceDisplay }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.points') }}</td>
                  <td>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ points }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </f7-block>
    </f7-page-content>

    <div class="sheet-footer">
      <f7-button v-if="!pooling_is_linked" @click="resetAndNavigate" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.linkpooling') }}</f7-button>
      <f7-button v-else-if="isDisabled" @click="noLogin" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.bookride') }}</f7-button>
      <f7-button v-else @click="bookRide" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.bookride') }}</f7-button>
    </div>

  </f7-sheet>
</template>

<script>
  import { f7, f7Sheet, f7BlockTitle, f7Block, f7ready, theme } from 'framework7-vue';
  import axios from 'axios';

  import car from "../assets/placeholder/images/car.png";

  export default {
      props: {
        title: String,
      },
      components: {
        f7Sheet,
        f7BlockTitle,
        f7Block
      },
      data() {
          return {
            placeholder: car,
            accessToken: this.$store.getters.getMapboxToken,
            mapboxAPI: this.$store.getters.getMapboxApi,
            mapboxCyclingURI: this.$store.getters.getMapboxCyclingURI,
            mapboxDrivingURI: this.$store.getters.getMapboxDrivingURI,
            selectedRideOption: {},
            selectedRideOptionUnformated: {},
            poolingRideOfferURL: this.$store.getters.getPoolingRideOffer,
            destination: {},
            distance: 0,
            points: 0,
            isDisabled: true
          };
      },
      computed: {
        inAppBrowser() {
          return this.$store.getters.getPluginInAppBrowser;
        },
        phone_unverified() {
          return this.$store.getters.getUserPhoneUnverified;
        },
        email_unverified() {
          return this.$store.getters.getUserEmailUnverified;
        },
        pooling_is_linked() {
          return this.$store.getters.getPoolingIsLinked;
        },
        hapticFeedback() {
          return this.$store.getters.getPluginHaptic;
        },
        distanceDisplay() {
          const m = this.distance;
          if (m == null) return '';
          if (m < 1000) return `${Math.round(m)} ${this.$t('planning.sheet.ridebooking.distanceunit')}`;
          return `${(m / 1000).toFixed(1)} ${this.$t('planning.sheet.ridebooking.rangedistanceunit')}`;
        }
      },
      created() {
          this.emitter.on('set-ride-booking-car', (options) => {
            this.selectedRideOption = { ...options.selectedRideOption };
            this.selectedRideOptionUnformated = options.selectedRideOptionUnformated;
            this.destination = options.destination;

            console.log("SELECTED RIDE: ", this.selectedRideOption);
            console.log("SELECTED RIDE UNFORMATED: ", this.selectedRideOptionUnformated);
            console.log("DESTINATION: ", this.destination);
          });
      },
      methods: {
        init() {
          console.log("SHEET RIDE BOOKING CAR SHARE OPENED!");
          const token = this.$store.getters.getUserToken;
          if (token !== null && token !== '') {
            this.isDisabled = false;
          }
          const directionsStart = [this.destination.geoLocation.longitude, this.destination.geoLocation.latitude];
          const directionsEnd = [this.destination.destLongitude, this.destination.destLatitude];
          this.getDirections(directionsStart, directionsEnd);
        },
        onClose() {
          console.log("SHEET CLOSING")
          this.isDisabled = true;
        },
        async getDirections(start, end) {
          try {
              const url = `${this.mapboxAPI}${this.mapboxCyclingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;

              const response = await axios.get(url);
              const data = response.data;

              this.distance = data.routes[0].distance;

              let tripData = {
                trip_mode:  'car',
                distance_m: this.distance
              }
              const responsePointEstimate = await bookingService.pointsEstimate(tripData);
              if (responsePointEstimate.status === 200) {
                this.points = Math.floor(responsePointEstimate.data.points_estimate);
              }
          } catch (error) {
              console.error('Error fetching directions:', error);
          }
        },
        async bookRide() {
          try {
            if (this.phone_unverified || this.email_unverified) {
              this.emitter.emit('show-verify-toast');
            } else {
              f7.dialog.confirm(this.$t('planning.sheet.ridebooking.dialog.booking-trip-link'), async () => {
                const pickupLongitude = this.selectedRideOption.pickup_longitude;
                const pickupLatitude = this.selectedRideOption.pickup_latitude;
                const dropOffLongitude = this.selectedRideOption.dropoff_longitude;
                const dropOffLatitude = this.selectedRideOption.dropoff_latitude;
                const departureTime = this.formatTime(this.selectedRideOptionUnformated.rideTimestamp, 'de-DE');
                const departureDate = this.formatDate(this.selectedRideOptionUnformated.rideTimestamp, 'de-DE');
                const departureDateTime = this.formatDateTime(this.selectedRideOptionUnformated.rideTimestamp, 'de-DE');
                const url = `${this.poolingRideOfferURL}${this.selectedRideOption.providerId}/?start=${pickupLongitude},${pickupLatitude}&destination=${dropOffLongitude},${dropOffLatitude}&departureTime=${departureTime}&departureDate=${departureDate}&departureDateTime=${departureDateTime}`;
                if (this.inAppBrowser) {
                  this.inAppBrowser.open(url, '_system');
                }
                await this.reset();
                this.navigateToPage('/activity');
              }, async () => { 
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
                await this.reset();
              })
            }
          } catch(err) {
            console.log("ERROR: ", err)
          }
        },
        noLogin() {
          let message = `<div class="dialog-icon-container">
                          <i class="f7-icons dialog-icon-warning">exclamationmark_triangle</i>
                        </div><br/>` + this.$t('app.dialog.error.not-logged-in');

          f7.dialog.confirm(message, async () => {
            await this.reset();
            this.navigateToPage('/login');
          });
        },
        formatDate(timestamp, locale) {
          let date = new Date(timestamp);
          const options = {
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit'
          };
          const formatter = new Intl.DateTimeFormat(locale, options);
          const parts = formatter.formatToParts(date);

          return `${parts[4].value}-${parts[2].value}-${parts[0].value}`;
        },
        formatTime(timestamp, locale) {
          let date = new Date(timestamp);
          return new Intl.DateTimeFormat(locale, { hour: '2-digit', minute: '2-digit' }).format(date);
        },
        formatDateTime(timestamp, locale) {
          let date = new Date(timestamp);
          const options = {
            timeZone: 'Europe/Berlin',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
          };

          const formatter = new Intl.DateTimeFormat(locale, options);
          const parts = formatter.formatToParts(date);

          const offset = -date.getTimezoneOffset();
          const hours = String(Math.floor(Math.abs(offset) / 60)).padStart(2, '0');
          const minutes = String(Math.abs(offset) % 60).padStart(2, '0');
          const sign = offset >= 0 ? '+' : '-';
          const timezoneOffset = `${sign}${hours}:${minutes}`;

          return `${parts[4].value}-${parts[2].value}-${parts[0].value}T${parts[6].value}:${parts[8].value}:${parts[10].value}${timezoneOffset}`;
        },
        async reset() {
          return new Promise((resolve) => {
            f7.sheet.close('.ride-options-sheet');
            f7.sheet.close('.ride-booking-car');
            setTimeout(() => {
              resolve();
            }, 350);
          });
        },
        openSheet() {
            f7.sheet.open('.ride-booking-car');
        },
        closeSheet() {
          this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
          f7.sheet.close('.ride-booking-car');
        },
        resetAndNavigate() {
          f7.sheet.close('.ride-booking-car');
          f7.sheet.close('.ride-options-sheet');
          f7.view.current.router.navigate('/carPoolSetup', { history: false, clearPreviousHistory: true, ignoreCache: true });
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
          this.emitter.off('set-ride-booking-car');
      },
  };
</script>