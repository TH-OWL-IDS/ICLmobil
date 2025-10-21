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
              style="min-height: 550px"
              swipe-to-close 
              push 
              backdrop 
              :close-by-backdrop-click="true" 
              :close-by-outside-click="true" 
              class="workAddress">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar-top">
            <div class="left sheet-title">
                {{ this.$t('account.sheet.workadress.title') }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-toolbar class="sheet-toolbar">
            <div class="searchbar searchbar-inner sheet-searchbar">
                <div class="searchbar-input-wrap">
                    <input type="search" 
                        :placeholder="this.$t('account.sheet.workadress.map.search.placeholder')"
                        @input="onInput" 
                        @focus="onFocus"
                        @keyup.enter="onEnter"
                        v-model="searchQuery" />
                    <i class="searchbar-icon"></i>
                    <span class="input-clear-button" @click="clearSearch"></span>
                </div>
            </div>
        </f7-toolbar>

        <f7-page>
            <div class="result-wrapper" v-if="searchResults.length && showResults">
                <f7-block-title medium>{{ this.$t('planning.sheet.yourdestination.resultstitle') }}</f7-block-title>
                <f7-list>
                    <div v-for="(result, index) in searchResults" :key="index">
                        <f7-list-item link="#" @click="handlePickResult(result)" :title="`${result.name}`">
                            <template #media>
                                <f7-icon ios="f7:map_pin_ellipse" md="material:pin_drop"></f7-icon>
                            </template>
                        </f7-list-item>
                    </div>
                </f7-list>
            </div>

            <div class="map-wrapper">
                <div v-if="mapOverlayEnabled" class="map-overlay">{{ mapDisabledText }}</div>
                <div ref="mapContainer" class="map-container"></div>
            </div>

            <f7-list inset class="no-padding-top no-margin-top no-padding-bottom no-margin-bottom">
                <f7-list-input 
                    :label="this.$t('account.page.favorites.sheet.newfavorite.fastStartOption.label')" 
                    type="select" 
                    v-model:value="localFavorite.rideOption"
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
                <f7-button href="#" :disabled="isLocalFavoriteEmpty" @click="saveAddress" fill large style="--f7-button-large-text-transform: none"><f7-icon ios="f7:checkmark_alt_circle_fill" md="material:check_circle"></f7-icon>&nbsp;{{ this.$t('account.sheet.workadress.button.saveaddress') }}</f7-button>
            </div>
        </f7-page>
    </f7-sheet>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';
    import $ from "dom7";

    import { calculateDistance } from '../js/utilities/utils';

    import mapboxgl from 'mapbox-gl';
    import FontawesomeMarker from "mapbox-gl-fontawesome-markers";
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
                title: "ArbeitsAdresse",
                accessToken: this.$store.getters.getMapboxToken,
                mapboxAPI: this.$store.getters.getMapboxApi,
                mapboxPlacesURI: this.$store.getters.getMapboxPlacesURI,
                countryCode: 'DE',
                map: null,
                geoLocator: null,
                geoLocation: null,
                toastWaitLocation: null,
                searchLimit: 3,
                searchRadius: 100000,
                favoriteMarker: [],
                searchMarker: [],
                searchQuery: '',
                searchResults: [],
                localFavorite: {},
                fastStartOption: null,
                debounceTimer: null,
                debounceTimeout: 500,
                showResults: false,
                mapOverlayEnabled: true,
                mapDisabledText: ''
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
            isLocalFavoriteEmpty() {
                return Object.keys(this.localFavorite).length === 0;
            },
            favorites: {
                get() {
                    return this.$store.getters.getFavorites;
                }
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        methods: {
            init() {
                console.log("SHEET WORK ADRESS OPENED");
                this.drawMap();
                this.resetSearch();

                this.showToastWait(this.$t('planning.toast.geolocate'));
                if (this.geoLocation) {
                    this.closeToastWait();
                    this.addFavoritesToMap();
                }
            },
            onClose() {
                console.log("SHEET CLOSING")
                this.closeToastWait();
                this.mapOverlayEnabled = true;
                this.mapDisabledText = '';
                this.localFavorite = {};
                this.fastStartOption = null;
                this.geoLocator = null;
                this.geoLocation = null;
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
                    minZoom: 10
                });

                // GEO LOCATION
                this.geoLocator = new mapboxgl.GeolocateControl({
                    positionOptions: {
                        enableHighAccuracy: true
                    },
                    trackUserLocation: true,
                    showUserHeading: true
                });
                map.addControl(this.geoLocator, 'bottom-right');

                this.geoLocator.on('geolocate', async (position) => {
                    this.closeToastWait();
                    this.enableMap();

                    this.geoLocation = position.coords;
                    this.goToFavoritePosition();
                });

                this.geoLocator.on('error', async (position) => {
                    this.mapDisabledText = this.$t('account.sheet.workadress.map-not-available');;
                    this.closeToastWait();
                });

                this.map = map;

                map.on('load', () => {
                    map.resize();
                    this.geoLocator.trigger();
                    this.addFavoritesToMap();
                });
            },
            disableMap() {
                this.mapOverlayEnabled = true;
                this.map.dragRotate.disable();
                this.map.scrollZoom.disable();
                this.map.boxZoom.disable();
                this.map.keyboard.disable();
                this.map.dragPan.disable();
                this.map.touchZoomRotate.disable();
            },
            enableMap() {
                this.map.dragRotate.enable();
                this.map.scrollZoom.enable();
                this.map.boxZoom.enable();
                this.map.keyboard.enable();
                this.map.dragPan.enable();
                this.map.touchZoomRotate.enable();
                this.mapOverlayEnabled = false;
            },
            async handleSearch(query) {
                try {
                    if (!query) return;
                    this.showResults = true;
                    const proximity = `${this.geoLocation.longitude},${this.geoLocation.latitude}`;
                    const response = await fetch(`${this.mapboxAPI}${this.mapboxPlacesURI}${encodeURIComponent(query)}.json?country=${this.countryCode}&access_token=${this.accessToken}&limit=${this.searchLimit}&proximity=${proximity}`);

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const data = await response.json();
                    const mapboxResults = data.features || [];

                    let results = mapboxResults.map(feature => ({
                        name: feature.place_name || '',
                        coordinates: feature.geometry.coordinates,
                        lat: feature.geometry.coordinates[1],
                        long: feature.geometry.coordinates[0],
                        placeType: feature.place_type[0],
                    }));

                    let filteredResults = results.filter(result => {
                        const distance = calculateDistance(this.geoLocation.latitude, this.geoLocation.longitude, result.lat, result.long);
                        return distance <= this.searchRadius;
                    });

                    this.searchResults = filteredResults;
                    this.showResults = true;
                    console.log("searchResults: ", this.searchResults)
                } catch (error) {
                    console.error('Error during search:', error);
                }
            },
            async handlePickResult(result) {
                try {
                    if (!result) return;
                    this.clearFavoriteMarker();
                    this.clearSearchMarker();
                    this.searchQuery = result.name;
                    this.showResults = false;
                    let markerIcon = 'fa-solid fa-briefcase';

                    const marker = new FontawesomeMarker({
                        draggable: false,
                        icon: markerIcon,
                        iconColor: '#fff',
                        color: '#99aa00',
                        scale: 1
                    })
                        .setLngLat([result.long, result.lat])
                        .addTo(this.map);

                    this.searchMarker.push(marker);

                    const popup = new mapboxgl.Popup({
                        closeButton: false, 
                        offset: {
                            'top': [0, 10],
                            'bottom': [0, -30],
                            'left': [10, 0],
                            'right': [-10, 0]
                        }, 
                        className: 'search-location-popup' })
                        .setHTML(`
                            <div class="search-location-popup-text">
                                ${result.name}
                            </div>`)
                        .setLngLat([result.long, result.lat])
                        .addTo(this.map);

                    marker.setPopup(popup);

                    this.map.flyTo({ 
                        center: [result.long, result.lat], 
                        zoom: 14,
                        offset: [0, 0],
                        speed: 2,
                        curve: 1.5,
                    });

                    let resultID = this.favorites.length + 1;
                    const index = this.favorites.findIndex(favorite => favorite.type === 'Work');
                    if (index !== -1) {
                        resultID = this.favorites[index].id;
                    }

                    this.localFavorite  = {
                        id: resultID,
                        address: result.name,
                        type: 'Work',
                        lat: result.lat,
                        long: result.long,
                        icon: "f7:bag"
                    };
                    console.log("NEW LOCAL FAV: ", this.localFavorite)
                } catch (error) {
                    console.error('ERROR: ', error);
                }
            },
            saveAddress() {
                if (Object.keys(this.localFavorite).length === 0) {
                    return;
                }
                const index = this.favorites.findIndex(favorite => favorite.type === 'Work');
                if (index !== -1) {
                    this.favorites[index] = { ...this.favorites[index], ...this.localFavorite };
                    console.log(`Work updated:`, this.favorites[index]);
                } else {
                    this.favorites.unshift(this.localFavorite);
                    console.log(`Work added:`, this.localFavorite);
                }
                this.sendHapticFeedback('CONFIRM', 'Success');
                this.$store.dispatch('setFavorites', { favorites: this.favorites });
                this.closeSheet();
            },
            goToFavoritePosition() {
                if (!this.favorites) return;
                this.favorites.forEach(favorite => {
                    if (favorite.type == 'Work') {
                        this.map.flyTo({ 
                            center: [favorite.long, favorite.lat], 
                            offset: [0, 0],
                            speed: 2,
                            curve: 1.5,
                            zoom: this.map.getZoom(),
                            essential: true,
                        });
                    }
                });
            },
            addFavoritesToMap() {
                if (!this.favorites) return;

                this.favorites.forEach(favorite => {
                    if (favorite.type == 'Work') {
                        let markerIcon = 'fa-solid fa-briefcase';

                        const marker = new FontawesomeMarker({
                            draggable: false,
                            icon: markerIcon,
                            iconColor: '#fff',
                            color: '#99aa00',
                            scale: 1
                        })
                            .setLngLat([favorite.long, favorite.lat])
                            .addTo(this.map);

                        this.favoriteMarker.push(marker);

                        this.localFavorite  = {
                            id: favorite.id,
                            address: favorite.address,
                            type: 'Work',
                            lat: favorite.lat,
                            long: favorite.long,
                            icon: "f7:bag",
                            rideOption: favorite.rideOption
                        };
                    }
                });
            },
            onInput(event) {
                this.searchQuery = event.target.value;

                if (this.searchQuery.trim() === '') {
                    this.clearSearch();
                }

                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.handleSearch(this.searchQuery);
                }, this.debounceTimeout);
            },
            onFocus() {
                this.sendHapticFeedback("SEGMENT_TICK", "SelectionChanged");
            },
            onEnter(event) {
                event.preventDefault();
                event.stopPropagation();
                this.handleSearch(this.searchQuery);
            },
            resetSearch() {
                if (this.searchMarker.length > 0) {
                    this.searchMarker.forEach(marker => marker.remove());
                }
                if (this.searchQuery) {
                    this.searchQuery= '';
                    this.searchResults = [];
                    this.searchMarker = [];
                    this.showResults = false;
                }
            },
            clearSearch() {
                this.searchQuery = '';
                this.searchResults = [];
                this.clearSearchMarker();
            },
            clearSearchMarker() {
                this.searchMarker.forEach(marker => marker.remove());
                this.searchMarker = [];
            },
            clearFavoriteMarker() {
                this.favoriteMarker.forEach(marker => marker.remove());
                this.favoriteMarker = [];
            },
            showToastWait(text) {
                this.toastWaitLocation = f7.toast.create({
                    text: text,
                    destroyOnClose: true,
                    icon: '<i class="f7-icons">location_circle_fill</i>',
                    position: 'center'
                });
                this.toastWaitLocation.open();
            },
            closeToastWait() {
                if (!this.toastWaitLocation) return;

                this.toastWaitLocation.close();
                const toastElement = $('.toast-center');
                if (toastElement) {
                    toastElement.remove();
                }
                this.toastWaitLocation = null;
            },
            closeSheet() {
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
                f7.sheet.close('.workAddress');
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
    .result-wrapper {
        position: absolute;
        z-index: 9999;
        height: 240px;
        width: 100vw;
        background-color: rgba(var(--f7-toolbar-bg-color-rgb, var(--f7-bars-bg-color-rgb)), var(--f7-bars-translucent-opacity));
    }
    .map-wrapper {
        display: flex;
        flex-direction: column;
        height: 250px;
        padding: 20px 20px 10px 20px;
        box-sizing: border-box;
    }
    .map-overlay {
        transition: background-color 1.0s;
        position: absolute;
        height: 200px;
        width: calc(100vw - 80px);
        background: rgba(128, 128, 128, 0.7);
        color: rgba(255, 255, 255, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 20px 20px 10px 20px;
        font-size: 24px;
        line-height: 1.3em;
        z-index: 10;
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
    :deep(.mapboxgl-ctrl-top-center) {
        position: absolute !important;
        top: 0;
        width: 100%;
        padding: 0 20px; /* Set padding here to center the search box */
        display: block;
        pointer-events: none;
        z-index: 2;
    }
    :deep(.mapboxgl-ctrl-top-center .mapboxgl-ctrl) { 
        margin: 20px auto;
    }
    .sheet-toolbar-top {
        height: 60px;
        z-index: -1;
    }
    .sheet-toolbar-pagecolor {
        height: 40px;
        background-color: var(--f7-page-bg-color) !important;
        z-index: -1;
    }
    .sheet-toolbar {
        height: 65px;
        background-color: transparent !important;
        z-index: -1;
    }
    .sheet-toolbar .searchbar {
        padding-top: 20px;
    }
    .button-wrapper {
        padding: 20px;
    }
</style>