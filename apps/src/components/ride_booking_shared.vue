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
            class="ride-booking-shared">
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
          <div style="text-align: center"><img :src="placeholder" style="max-width: 70%; height: auto;"/></div>
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
                <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.model') }}</td>
                <td>{{ selectedRideOption.vehicleModel }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.id') }}</td>
                  <td>{{ selectedRideOption.vehicleId }} - {{ selectedRideOption.vehicleNumber }}</td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.stateofcharge') }}</td>
                  <td>
                    <div v-if="!selectedRideOption.stateOfCharge">{{ this.$t('planning.sheet.ridebooking.unknown') }}</div>
                    <div v-else>{{ selectedRideOption.stateOfCharge }}%</div>
                  </td>
              </tr>
              <tr>
                  <td class="label-cell table-text-bold">{{ this.$t('planning.sheet.ridebooking.range') }}</td>
                  <td>
                    <div v-if="!selectedRideOption.remainingRangeKm">{{ this.$t('planning.sheet.ridebooking.unknown') }}</div>
                    <div v-else>{{ this.$t('planning.sheet.ridebooking.approximate') }} {{ selectedRideOption.remainingRangeKm }} {{ this.$t('planning.sheet.ridebooking.rangedistanceunit') }}</div>
                  </td>
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
        <div class="map-wrapper">
          <div ref="mapContainer" class="map-container"></div>
          <div class="map-overlay"></div>
        </div>
        <div class="map-hint">{{ this.$t('planning.sheet.ridebooking.hint1') }} {{ distanceDisplay }}.
          {{ this.$t('planning.sheet.ridebooking.hint2') }} {{ points }} <div v-html="$t('planning.sheet.ridebooking.hint3')" style="display: inline;"></div>
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

  import mapboxgl from 'mapbox-gl';
  import '../../node_modules/mapbox-gl/dist/mapbox-gl.css';
  import axios from 'axios';

  import bookingService from '../services/bookingService';

  import scooter from "../assets/placeholder/images/scooter.png";
  import bike from "../assets/placeholder/images/bike.png";

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
            placeholder: scooter,
            accessToken: this.$store.getters.getMapboxToken,
            mapboxAPI: this.$store.getters.getMapboxApi,
            mapboxCyclingURI: this.$store.getters.getMapboxCyclingURI,
            map: null,
            directionsStart: [],
            directionsEnd: [],
            selectedRideOption: {},
            selectedRideOptionUnformated: {},
            destination: {},
            distance: 0,
            points: 0,
            isDisabled: true,
            rentalPeriodDefault: 4,
            rentalPeriodPicked: null,
            rentalPeriodPicker: null
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
          this.emitter.on('set-ride-booking-shared', (options) => {
              this.selectedRideOption = options.selectedRideOption;
              this.selectedRideOptionUnformated = options.selectedRideOptionUnformated;
              this.destination = options.destination;

              console.log("SELECTED RIDE: ", this.selectedRideOption);
              console.log("SELECTED RIDE UNFORMATED: ", this.selectedRideOptionUnformated);
              console.log("DESTINATION: ", this.destination);

              switch(this.selectedRideOption.vehicleType) {
                case "scooter":
                  this.placeholder = scooter;
                  break;
                case "bike":
                  this.placeholder = bike;
                  break;
                default:
                  this.placeholder = scooter;
                  break;
              }
          });
      },
      methods: {
        init() {
          console.log("SHEET RIDE BOOKING SHARED OPENED!")
          this.drawMap();
          const token = this.$store.getters.getUserToken;
          if (token !== null && token !== '') {
            this.isDisabled = false;
          }
        },
        onClose() {
          console.log("SHEET CLOSING")
          this.isDisabled = true;
          this.map.remove();
          this.map = null;
          this.rentalPeriodPicked = null;
        },
        drawMap() {
          mapboxgl.accessToken = this.accessToken;
          const map = new mapboxgl.Map({
              container: this.$refs.mapContainer,
              style: this.$store.getters.getMapboxStyle,
              center: [8.90500, 52.01750],
              zoom: 13,
              minZoom: 6,
          });

          this.map = map;

          map.on('load', () => {
              this.map.resize();
              const directionsStart = [this.destination.geoLocation.longitude, this.destination.geoLocation.latitude];
              const directionsEnd = [this.destination.destLongitude, this.destination.destLatitude];
              this.getDirections(directionsStart, directionsEnd);
          });
        },
        async getDirections(start, end) {
          try {
              const url = `${this.mapboxAPI}${this.mapboxCyclingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;

              const response = await axios.get(url);
              const data = response.data;

              this.distance = data.routes[0].distance;

              let tripData = {
                trip_mode:  'sharing',
                distance_m: this.distance
              }
              const responsePointEstimate = await bookingService.pointsEstimate(tripData);
              if (responsePointEstimate.status === 200) {
                this.points = Math.floor(responsePointEstimate.data.points_estimate);
              }

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
        async bookRide() {
          try {
            if (this.phone_unverified || this.email_unverified) {
              this.emitter.emit('show-verify-toast');
            } else {
              if (!this.rentalPeriodPicked) {
                this.showTimePicker();
              } else {
                let data = {
                  trip_mode: this.selectedRideOption.optionType,
                  state: "planned",
                  from_location_latitude: this.destination.geoLocation.latitude,
                  from_location_longitude: this.destination.geoLocation.longitude,
                  from_description: this.destination.userPlaceName,
                  to_location_latitude: this.destination.destLatitude,
                  to_location_longitude: this.destination.destLongitude,
                  to_description: this.destination.destPlaceName,
                  start_time: this.selectedRideOptionUnformated.rideTimestamp,
                  end_time: this.selectedRideOptionUnformated.approxTimeOfArrival,
                  vehicle_id: this.selectedRideOption.vehicleId
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
        showTimePicker() {
          const self = this;
          
          const maxDuration = self.selectedRideOption.maximumDurationH || self.rentalPeriodDefault;
          const values = [];
          for (let i = 0.5; i <= maxDuration; i += 0.5) {
            values.push(i.toString());
          }
          
          self.rentalPeriodPicker = f7.picker.create({
            rotateEffect: true,
            renderToolbar() {
              return (
                '<div class="toolbar">' +
                '<div class="toolbar-inner">' +
                '<div class="left" style="margin-left: 8px;">' +
                '<a class="link picker-toolbar-book-link">' + self.$t('planning.sheet.ridebooking.picker.link') + '</a>' +
                '</div>' +
                '<div class="center">' +
                '<div style="display: flex; align-items: center; font-size: 18px; font-weight: 500;">' +
                self.$t('planning.sheet.ridebooking.picker.title') +
                '</div>' +
                '</div>' +
                '<div class="right">' +
                '<a class="link sheet-close popover-close"><i class="f7-icons" style="color: #ccc !important;">multiply_circle_fill</i></a>' +
                '</div>' +
                '</div>' +
                '</div>'
              );
            },
            cols: [
              {
                textAlign: 'center',
                values: values,
                onChange(picker, time) {
                  const startDate = new Date(self.selectedRideOptionUnformated.approxTimeOfArrival);
                  const hoursToAdd = parseFloat(time);
                  startDate.setHours(startDate.getHours() + hoursToAdd);
                  self.selectedRideOptionUnformated.approxTimeOfArrival = startDate.toISOString();
                  self.rentalPeriodPicked = time;
                }
              },
              {
                divider: true,
                content: self.$t('planning.sheet.ridebooking.picker.unit'),
              },
            ],
            on: {
              open(picker) {
                picker.$el.find('.picker-toolbar-book-link').on('click', function () {
                  self.bookRide();
                });
              },
              close(picker) {
                self.rentalPeriodPicked = null;
              }
            }
          });
          self.rentalPeriodPicker.open();
        },
        closeTimePicker() {
          if (this.rentalPeriodPicker) {
            this.rentalPeriodPicker.close();
          }
        },
        async reset() {
          return new Promise((resolve) => {
            this.closeTimePicker();
            f7.sheet.close('.ride-options-sheet');
            f7.sheet.close('.ride-booking-shared');
            setTimeout(() => {
              resolve();
            }, 350);
          });
        },
        openSheet() {
          f7.sheet.open('.ride-booking-shared');
        },
        closeSheet() {
          this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
          f7.sheet.close('.ride-booking-shared');
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
          this.emitter.off('set-ride-booking-shared');
      },
  };
</script>
<style scoped>
    .map-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.5);
        display: flex;
        padding: 20px;
        z-index: 10;
    }
    .map-wrapper :deep(canvas.mapboxgl-canvas) {
      filter: grayscale(100%) brightness(1) contrast(1);
    }
    .map-hint {
        color: rgba(100, 150, 150, 1);
        font-size: 12px;
        padding: 10px;
    }
    .map-wrapper {
        display: flex;
        flex-direction: column;
        height: 220px;
        margin-top: 10px;
        box-sizing: border-box;
        position: relative;
    }
    .map-container {
        flex-grow: 1;
        width: 100%;
        box-sizing: border-box;
        position: relative;
    }
</style>