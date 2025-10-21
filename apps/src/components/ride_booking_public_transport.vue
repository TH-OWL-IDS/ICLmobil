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
            swipe-to-close 
            style="height: 90vh" 
            :close-by-backdrop-click="false" 
            :close-by-outside-click="false" 
            class="ride-booking-public-transport">
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
                <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.line') }}</td>
                <td>{{ selectedRideOption.rideOption }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.distance') }}</td>
                  <td>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ distanceDisplay }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.points') }}</td>
                  <td>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ points }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.ridetails') }}</td>
                  <td>
                    <div class="accordion-item">
                      <div class="accordion-item-toggle"><f7-button href="#" class="timelineButton" round tonal><f7-icon size="15" ios="f7:info_circle_fill" md="material:info"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.ridedetails') }}</f7-button></div>
                      <div class="accordion-item-content"><div v-html="createTimeline(selectedRideOption)"></div></div>
                    </div>
                  </td>
              </tr>
            </tbody>
          </table>
        </div>
      </f7-block>
    </f7-page-content>

    <div class="sheet-footer">
      <f7-button v-if="isDisabled" @click="noLogin" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.bookride') }}</f7-button>
      <f7-button v-else @click="bookRide" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.bookride') }}</f7-button>
    </div>

  </f7-sheet>
</template>

<script>
  import { f7, f7Sheet, f7BlockTitle, f7Block, f7ready, theme } from 'framework7-vue';
  import axios from 'axios';
  import bookingService from '../services/bookingService';

  import bus from "../assets/placeholder/images/bus.png";

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
            placeholder: bus,
            accessToken: this.$store.getters.getMapboxToken,
            mapboxAPI: this.$store.getters.getMapboxApi,
            mapboxCyclingURI: this.$store.getters.getMapboxCyclingURI,
            mapboxDrivingURI: this.$store.getters.getMapboxDrivingURI,
            selectedRideOption: {},
            selectedRideOptionUnformated: {},
            destination: {},
            distance: 0,
            points: 0,
            isDisabled: true
          };
      },
      computed: {
        phone_unverified() {
          return this.$store.getters.getUserPhoneUnverified;
        },
        email_unverified() {
          return this.$store.getters.getUserEmailUnverified;
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
          this.emitter.on('set-ride-booking-public-transport', (options) => {
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
          console.log("SHEET RIDE BOOKING PUBLIC TRANSPORT OPENED!")
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
            f7.accordion.close('.accordion-item');
            this.isDisabled = true;
        },
        createTimeline(selectedRide) {
          let timelineHTML = '<div class="timeline">';
          if (selectedRide.journey) {
            console.log("JOURNEY: ", selectedRide.journey);
            if (selectedRide.journey.legs.length > 0) {
              console.log("LEGS: ", selectedRide.journey.legs);

              selectedRide.journey.legs.forEach(section => {
                  const modeOfTransport = section.mode_of_transport.description;
                  const fromName = section.from_name;
                  const toName = section.to_name;
                  const duration = section.duration_s / 60;
                  const line = section.pt_line != null ? section.pt_line : "";

                  const icon = modeOfTransport === 'Foot way' ? 'directions_walk' : 'directions_bus';
                  const transportTranslations = {
                      'Foot way': this.$t('planning.sheet.ridebooking.footway'),
                      'city bus': this.$t('planning.sheet.ridebooking.citybus'),
                      'regional bus': this.$t('planning.sheet.ridebooking.regionalbus'),
                      'regional train': this.$t('planning.sheet.ridebooking.regionaltrain'),
                      'transit on call': this.$t('planning.sheet.ridebooking.transitoncall')
                  };

                  const modeOfTransportTrans = transportTranslations[modeOfTransport] || modeOfTransport;

                  timelineHTML += `
                      <div class="timeline-section">
                          <div class="icon-wrapper">
                              <i class="material-icons">${icon}</i>
                          </div>
                          <h3>${modeOfTransportTrans} ${line}</h3>
                          <b>` + this.$t('planning.sheet.ridebooking.from') + `:</b> ${fromName}<br />
                          <b>` + this.$t('planning.sheet.ridebooking.to') + `:</b> ${toName}<br />
                          <b>` + this.$t('planning.sheet.ridebooking.duration') + `:</b> ${duration} ` + this.$t('planning.sheet.ridebooking.minutes') + `<br />
                      </div>
                  `;
              });
              timelineHTML += '</div>';
            }
          }
          return timelineHTML;
        },
        async getDirections(start, end) {
          try {
              const url = `${this.mapboxAPI}${this.mapboxCyclingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;

              const response = await axios.get(url);
              const data = response.data;

              this.distance = data.routes[0].distance;

              let tripData = {
                trip_mode:  'pt',
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
              let data = {
                trip_mode: this.selectedRideOption.optionType,
                state: "planned",
                from_location_latitude: this.selectedRideOptionUnformated.journey.legs[0].to_location.latitude,
                from_location_longitude: this.selectedRideOptionUnformated.journey.legs[0].to_location.longitude,
                from_description: this.destination.userPlaceName,
                to_location_latitude: this.destination.destLatitude,
                to_location_longitude: this.destination.destLongitude,
                to_description: this.destination.destPlaceName,
                start_time: this.selectedRideOptionUnformated.rideTimestamp,
                end_time: this.selectedRideOptionUnformated.approxTimeOfArrival,
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
                await this.reset();
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
                await this.reset();
              }
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
        async reset() {
          return new Promise((resolve) => {
            f7.sheet.close('.ride-options-sheet');
            f7.sheet.close('.ride-booking-public-transport');
            setTimeout(() => {
              resolve();
            }, 350);
          });
        },
        openSheet() {
          f7.sheet.open('.ride-booking-public-transport');
        },
        closeSheet() {
          this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
          f7.sheet.close('.ride-booking-public-transport');
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
          this.emitter.off('set-ride-booking-public-transport');
      },
  };
</script>