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
            class="ride-booking-foot-way">
  <template #fixed>
    <div class="swipe-handler"></div>
  </template>

  <f7-toolbar class="sheet-toolbar">
        <div class="left sheet-title">
            {{ pageTitle }}
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
      <f7-button v-if="isDisabled" @click="noLogin" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.bookwalk') }}</f7-button>
      <f7-button v-else @click="bookRide" class="button-booking" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('planning.sheet.ridebooking.button.bookwalk') }}</f7-button>
    </div>

  </f7-sheet>
</template>

<script>
  import { f7, f7Sheet, f7BlockTitle, f7Block, f7ready, theme } from 'framework7-vue';

  import mapboxgl from 'mapbox-gl';
  import '../../node_modules/mapbox-gl/dist/mapbox-gl.css';
  import axios from 'axios';
  
  import bookingService from '../services/bookingService';

  import walk from "../assets/placeholder/images/walk.png";

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
            pageTitle: this.title,
            accessToken: this.$store.getters.getMapboxToken,
            mapboxAPI: this.$store.getters.getMapboxApi,
            mapboxWalkingURI: this.$store.getters.getMapboxWalkingURI,
            map: null,
            directionsStart: [],
            directionsEnd: [],
            placeholder: walk,
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
          this.emitter.on('set-ride-booking-foot-way', (options) => {
            this.selectedRideOption = { ...options.selectedRideOption };
            this.selectedRideOptionUnformated = options.selectedRideOptionUnformated;
            this.destination = options.destination;

            console.log("SELECTED RIDE: ", this.selectedRideOption);
            console.log("SELECTED RIDE UNFORMATED: ", this.selectedRideOptionUnformated);
            console.log("DESTINATION: ", this.destination);

            this.pageTitle = this.$t('planning.sheet.ridebooking.footway');
          });
      },
      methods: {
        init() {
          console.log("SHEET RIDE BOOKING WALK OPENED!")
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
              const directionsStart = [this.destination.geoLocation.longitude, this.destination.geoLocation.latitude];
              const directionsEnd = [this.destination.destLongitude, this.destination.destLatitude];
              this.getDirections(directionsStart, directionsEnd);
          });
        },
        async getDirections(start, end) {
          try {
              const url = `${this.mapboxAPI}${this.mapboxWalkingURI}${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${this.accessToken}`;

              const response = await axios.get(url);
              const data = response.data;

              this.distance = data.routes[0].distance;

              let tripData = {
                trip_mode:  'walk',
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
              let data = {
                trip_mode: this.selectedRideOptionUnformated.optionType,
                state: "planned",
                from_location_latitude: this.destination.geoLocation.latitude,
                from_location_longitude: this.destination.geoLocation.longitude,
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
            f7.sheet.close('.ride-booking-foot-way');
            setTimeout(() => {
              resolve();
            }, 350);
          });
        },
        openSheet() {
          f7.sheet.open('.ride-booking-foot-way');
        },
        closeSheet() {
          this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
          f7.sheet.close('.ride-booking-foot-way');
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
          this.emitter.off('set-ride-booking-foot-way');
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