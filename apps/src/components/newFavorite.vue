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
              style="min-height: 80vh" 
              swipe-to-close 
              push 
              backdrop 
              :close-by-backdrop-click="true" 
              :close-by-outside-click="true" 
              class="newFavorite">
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
            <div class="map-wrapper">
                <div ref="mapContainer" class="map-container"></div>
            </div>
            <f7-list dividers-ios strong inset class="no-padding-top no-margin-top no-padding-bottom no-margin-bottom">
                <f7-list-input
                    type="text"
                    :placeholder="this.$t('account.page.favorites.sheet.newfavorite.address.placeholder')"
                    :info="this.$t('account.page.favorites.sheet.newfavorite.address.info')"
                    v-model:value="localFavorite.address"
                >
                </f7-list-input>

                <f7-list-input
                    type="text"
                    :placeholder="this.$t('account.page.favorites.sheet.newfavorite.type.placeholder')"
                    :info="this.$t('account.page.favorites.sheet.newfavorite.type.info')"
                    v-model:value="localFavorite.type"
                >
                </f7-list-input>

                <f7-list-input 
                    :label="this.$t('account.page.favorites.sheet.newfavorite.fastStartOption.label')" 
                    type="select" 
                    v-model:value="fastStartOption"
                    data-cy="favorites-rideoption-fld"
                >
                    <option value="" disabled>
                        {{ this.$t('account.page.favorites.sheet.newfavorite.fastStartOption.placeholder') }}
                    </option>
                    <option 
                        v-for="option in fastStartOptions"
                        :key="option.id"
                        :value="option.type">
                    {{ option.string[this.$i18n.locale] }}
                    </option>
                </f7-list-input>
            </f7-list>

            <div class="button-wrapper">
                <f7-button href="#" :disabled="isLocalFavoriteValid" @click="saveFavorite" fill large style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_alt_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('account.page.favorites.sheet.newfavorite.button.savefavorite') }}</f7-button>
            </div>

            <f7-block>
                <f7-block-title medium></f7-block-title>
            </f7-block>
        </f7-page-content>
    </f7-sheet>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';

    import mapboxgl from 'mapbox-gl';
    import { MapboxSearchBox } from '@mapbox/search-js-web';
    import '../../node_modules/mapbox-gl/dist/mapbox-gl.css';
  
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
                title: this.$t('account.page.favorites.sheet.newfavorite.title'),
                mapboxAPI: this.$store.getters.getMapboxApi,
                mapboxPlacesURI: this.$store.getters.getMapboxPlacesURI,
                accessToken: this.$store.getters.getMapboxToken,
                searchQuery: '',
                toastWaitLocation: null,
                localFavorite: {},
                fastStartOption: null,
                markers: [],
                longPressTimer: null,
                longPressTime: 1500,
                isDragging: false,
                isPinching: false,
            };
        },
        watch: {
            fastStartOption: {
                handler() {
                    if (Object.keys(this.localFavorite).length > 0) {
                        this.localFavorite.rideOption = this.fastStartOption;
                    }
                },
                immediate: true,
            }
        },
        computed: {
            fastStartOptions: {
                get() {
                    return this.$store.getters.getFastStartOptions;
                }
            },
            favorites: {
                get() {
                    return this.$store.getters.getFavorites;
                }
            },
            isLocalFavoriteValid() {
                const requiredKeys = ["address", "type"];
                const localFavoriteKeys = Object.keys(this.localFavorite);

                const hasAllRequiredKeys = requiredKeys.every(key => localFavoriteKeys.includes(key));
                const isNotEmpty = localFavoriteKeys.length > 0;

                const allValuesPresent = requiredKeys.every(key => {
                    return this.localFavorite[key] !== undefined && this.localFavorite[key] !== null && this.localFavorite[key] !== '';
                });

                return !(hasAllRequiredKeys && isNotEmpty && allValuesPresent);
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        methods: {
            init() {
                console.log("SHEET NEW FAVORITE OPENED")
                console.log("LOCAL FAVORITE: ", this.localFavorite)
                this.drawMap();
            },
            onClose() {
                console.log("SHEET CLOSING")
                this.clearMarkers();
                this.localFavorite = {};
                this.fastStartOption = null;
                this.map.remove();
                this.map = null;
            },
            updateSearchResults(results) {
                this.searchResults = [...results];
            },
            drawMap() {
                mapboxgl.accessToken = this.accessToken;
                const map = new mapboxgl.Map({
                    container: this.$refs.mapContainer,
                    style: this.$store.getters.getMapboxStyle,
                    center: [8.90500, 52.01750],
                    zoom: 13,
                    minZoom: 8,
                    maxZoom: 20
                });

                const that = this;

                // SEARCH BOX
                const searchBox = new MapboxSearchBox();
                searchBox.accessToken = this.accessToken
                searchBox.options = {
                    types: 'address,poi',
                    proximity: [8.90500, 52.01750],
                    language: 'de',
                    limit: 2
                };
                const theme = {
                    variables: {
                        fontFamily: 'Avenir, sans-serif',
                        unit: '1.2em',
                        borderRadius: '4px',
                        lineHeight: '1.5em'
                    }
                };

                searchBox.theme = theme;
                searchBox.mapboxgl = mapboxgl;
                searchBox.placeholder = this.$t('account.page.favorites.sheet.newfavorite.map.search.placeholder');
                searchBox.bbox = this.$store.getters.getMapboxBBoxCoords;

                searchBox.bindMap(map);

                this.registerControlPosition(map, 'top-center');

                map.addControl(searchBox, 'top-center');

                searchBox.addEventListener('retrieve', (event) => {
                    const selectedLocation = event.detail;
                    const firstResult = selectedLocation.features[0];
                    const properties = firstResult.properties;
                    const long = firstResult.geometry.coordinates[0];
                    const lat = firstResult.geometry.coordinates[1];
                    const placeName = properties.full_address;
                    const placeType = properties.feature_type;

                    const destination = {
                        destLatitude: lat,
                        destLongitude: long,
                        destPlaceName: placeName,
                        destPlaceType: placeType,
                    };
                    this.handleSearch(destination);
                });

                this.map = map;

                map.on('load', () => {
                    map.resize();
                });

                this.map.on('movestart', () => {
                    this.isDragging = true;
                });

                this.map.on('moveend', () => {
                    this.isDragging = false;
                });

                // ADD EVENT HANDLER FOR MOUSE EVENTS TO ADD FAVORITES BY LONG PRESS
                const handlePressStart = (e) => {
                    this.isDragging = false;
                    
                    this.longPressTimer = setTimeout(() => {
                        if (!this.isDragging && !this.isPinching) {
                            const coordinates = e.lngLat || e.touches[0].lngLat;
                            this.addFavoriteMarker(coordinates);
                        }
                    }, this.longPressTime);
                    
                };
                const handlePressEnd = () => {
                    clearTimeout(this.longPressTimer);
                };

                this.map.on('mousedown', handlePressStart);
                this.map.on('mouseup', handlePressEnd);
                this.map.on('mouseleave', handlePressEnd);
                
                // ADD TOUCH EVENTS FOR ADDING FAVORITE MARKER
                map.on('touchstart', (e) => {
                    if (e.originalEvent.touches.length > 1) {
                        that.isPinching = true;
                        handlePressEnd();
                    } else {
                        handlePressStart(e);
                    }
                });

                map.on('touchmove', (e) => {
                    if (that.isPinching) {
                        handlePressEnd();
                    }
                });

                map.on('touchend', (e) => {
                    if (that.isPinching) {
                        that.isPinching = false;
                    } else {
                        handlePressEnd();
                    }
                });
            },
            async addFavoriteMarker(coordinates) {
                this.clearMarkers();
                const marker = new mapboxgl.Marker({
                    draggable: true,
                    color: "#99aa00",
                    scale: 1
                })
                    .setLngLat([coordinates.lng, coordinates.lat])
                    .addTo(this.map);

                var address = await this.getAddressFromCoordinates(coordinates);
                let favoriteID = this.addFavorite(coordinates, address);
                this.sendHapticFeedback("CONFIRM", "Success");

                marker.on('dragstart', () => {
                    this.isDragging = true;
                    this.sendHapticFeedback("CONFIRM", "Success");
                });

                marker.on('dragend', async () => {
                    this.isDragging = false;
                    const lngLat = marker.getLngLat();
                    var address = await this.getAddressFromCoordinates(lngLat);
                    this.changeFavorite(lngLat, address, favoriteID);
                    this.sendHapticFeedback("CONFIRM", "Success");
                });

                this.markers.push(marker);
            },
            async getAddressFromCoordinates(coordinates) {
                try {
                    const response = await fetch(`${this.mapboxAPI}${this.mapboxPlacesURI}${coordinates.lng},${coordinates.lat}.json?access_token=${this.accessToken}`);
                    if (!response.ok) {
                        this.clearMarkers();
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    const data = await response.json();
                    const address = data.features[0]?.place_name;
                    return address || 'Adresse nicht gefunden';
                } catch (error) {
                    this.clearMarkers();
                    console.error('Fehler beim Abrufen der Adresse:', error);
                    return 'Fehler beim Abrufen der Adresse';
                }
            },
            registerControlPosition(map, positionName) {
                if (map._controlPositions[positionName]) {
                    return;
                }
                var positionContainer = document.createElement('div');
                positionContainer.className = `mapboxgl-ctrl-${positionName}`;
                map._controlContainer.appendChild(positionContainer);
                map._controlPositions[positionName] = positionContainer;
            },
            closeSheet() {
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
                f7.sheet.close('.newFavorite');
            },
            handleSearch(destination) {
                this.localFavorite = { 
                    id: this.favorites.length + 1, 
                    address: destination.destPlaceName, 
                    type: destination.destPlaceType,
                    lat: destination.destLatitude,
                    long: destination.destLongitude,
                    icon: "f7:map_pin_ellipse" 
                };
            },
            addFavorite(coordinates, address) {
                var maxId = this.favorites.reduce((max, entry) => Math.max(max, entry.id), 0);
                var newID = maxId + 1;

                this.localFavorite = { 
                    id: newID, 
                    address: address, 
                    type: 'Adresse',
                    lat: coordinates.lat,
                    long: coordinates.lng,
                    icon: "f7:map_pin_ellipse",
                    rideOption: this.fastStartOption
                };
                return newID;
            },
            changeFavorite(coordinates, address, id) {
                this.localFavorite = { 
                    id: id, 
                    address: address, 
                    type: 'Adresse',
                    lat: coordinates.lat,
                    long: coordinates.lng,
                    icon: "f7:map_pin_ellipse",
                    rideOption: this.fastStartOption
                };
            },
            saveFavorite() {
                if (Object.keys(this.localFavorite).length === 0) {
                    return;
                }
                this.favorites.push(this.localFavorite);
                this.sendHapticFeedback("CONFIRM", "Success");
                this.$store.dispatch('setFavorites', { favorites: this.favorites });
                this.closeSheet();
            },
            clearMarkers() {
                this.markers.forEach(marker => marker.remove());
                this.markers = [];
            },
            sendHapticFeedback(androidType, iosType) {
                if (this.hapticFeedback) {
                    this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                        console.error("HAPTIC ERROR: ", error);
                    });
                }
            }
        },
    };
</script>

<style scoped>
    .map-wrapper {
        display: flex;
        flex-direction: column;
        height: 30vh;
        padding: 0 20px 10px;
        box-sizing: border-box;
    }
    .map-container {
        flex-grow: 1;
        width: 100%;
        box-sizing: border-box;
        position: relative;
    }
    :deep(.mapboxgl-ctrl-top-center input[type='text']) {
        padding-left: 40px !important;
    }
    :deep(.mapboxgl-ctrl-group) {
        position: relative;
        top: 60px !important;
    }
    :deep(.mapboxgl-ctrl-top-center .mapboxgl-ctrl) { 
        margin: 20px auto;
    }
    :deep(.mapboxgl-popup-content) {
        color: black !important;
    }
    .button-wrapper {
        padding: 20px 20px 20px 20px;
    }
</style>