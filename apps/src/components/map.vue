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
    <div v-if="mapOverlayEnabled" class="map-overlay">
        <div class="map-overlay-text-wrapper">
            <div class="map-overlay-text">{{ mapDisabledText }}</div>
            <div v-if="mapSettingsButton" class="map-overlay-link">
                <f7-button large fill @click="goToSettings">
                    <i class="fa-solid fa-location-arrow" style="color: white; font-size: 22px;"></i>&nbsp;
                    {{ this.$t('planning.map-show-settings') }}
                </f7-button>
            </div>
        </div>
    </div>
    <div ref="mapContainer" class="map-container"></div>
    <div id="trash-bin">
        <i id="trash-icon" class="fa fa-trash" style="color: white; font-size: 26px;"></i>
    </div>
</template>
<script>
    import { getDevice }  from 'framework7';
    import { f7, f7ready } from 'framework7-vue';
    import $ from "dom7";

    import mapboxgl from 'mapbox-gl';
    import FontawesomeMarker from "mapbox-gl-fontawesome-markers";
    import poiService from '../services/poiService';

    export default {
        props: {
            title: String,
            searchQuery: {
                type: String,
                default: '',
            },
        },
        data() {
            return {
                device: getDevice(),
                accessToken: this.$store.getters.getMapboxToken,
                mapboxAPI: this.$store.getters.getMapboxApi,
                mapboxPlacesURI: this.$store.getters.getMapboxPlacesURI,
                countryCode: 'DE',
                map: null,
                markers: [],
                favoritesMarker: [],
                searchResults: [],
                geoLocator: null,
                geoLocation: null,
                userAddress: null,
                toastWaitLocation: null,
                longPressTimer: null,
                longPressTime: 1500,
                markerText: this.$t('planning.marker.popup.text'),
                isDragging: false,
                isPinching: false,
                poiLimit: 5,
                searchLimit: 5,
                mapCenter: null,
                mapOverlayEnabled: true,
                mapSettingsButton: false,
                mapDisabledText: '',
                isEditFavoritesMode: false
            };
        },
        watch: {
            isEditFavoritesMode(newVal) {
                if (newVal) {
                    f7.toast.show({
                        text: `<i class="f7-icons" style="vertical-align:middle;margin-right:6px;">pencil</i>${this.$t('planning.edit-favorites-mode-active')}`,
                        position: 'top',
                        closeTimeout: 2000,
                        cssClass: 'edit-favorites-toast'
                    });
                } else {
                    f7.toast.show({
                        text: `<i class="f7-icons" style="vertical-align:middle;margin-right:6px;">pencil</i>${this.$t('planning.edit-favorites-mode-inactive')}`,
                        position: 'top',
                        closeTimeout: 2000,
                        cssClass: 'edit-favorites-toast'
                    });
                }
            },
            searchQuery: {
                handler(newQuery) {
                    this.handleSearch(newQuery);
                },
                immediate: true,
            },
        },
        created() {
            this.emitter.on('refresh-map-planning', () => {
                setTimeout(() => {
                    console.log("MAP RESIZE!");
                    this.map.resize();
                }, 300);
            });
            this.emitter.on('enable-edit-favorites', () => {
                this.isEditFavoritesMode = !this.isEditFavoritesMode;
                this.clearFavoriteMarkers();
                this.addFavoritesToMap();
            });
        },
        computed: {
            showRestaurants: {
                get() {
                    return this.$store.getters.getShowRestaurants;
                },
                set(value) {
                    this.$store.dispatch('setShowRestaurants', value);
                },
            },
            showBusStops: {
                get() {
                    return this.$store.getters.getShowBusStops;
                },
                set(value) {
                    this.$store.dispatch('setShowBusStops', value);
                },
            },
            showFavorites: {
                get() {
                    return this.$store.getters.getShowFavorites;
                },
                set(value) {
                    this.$store.dispatch('setShowFavorites', value);
                },
            },
            favorites: {
                get() {
                    return this.$store.getters.getFavorites;
                }
            },
            lastDestinations: {
                get() {
                    return this.$store.getters.getLastDestinations;
                }
            },
            diagnostic() {
                return this.$store.getters.getPluginDiagnostic;
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        mounted() {
            f7ready(async () => {
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

                // GEO LOCATION BUTTON
                this.geoLocator = new mapboxgl.GeolocateControl({
                    positionOptions: {
                        enableHighAccuracy: true
                    },
                    trackUserLocation: false,
                    showUserHeading: true
                });
                map.addControl(this.geoLocator, 'top-right');

                // CUSTOM SEARCH BUTTON
                class CustomSearchButton {
                    constructor() {
                        this.button = document.createElement('button');
                        this.button.className = 'mapbox-custom-button';
                        this.button.innerHTML = '<i class="material-icons" style="font-size: 32px;">search</i>';
                        this.button.title = "Open Search";

                        this.button.style.backgroundColor = '#fff';
                        this.button.style.color = '#000';
                        this.button.style.border = 'none';
                        this.button.style.borderRadius = '4px';
                        this.button.style.padding = '0';
                        this.button.style.cursor = 'pointer';
                        this.button.style.margin = '6px';

                        this.button.addEventListener('click', () => {
                            f7.sheet.close('.ride-options-sheet');
                            that.emitter.emit('showLastLocations', '');
                        });
                    }
                    onAdd(map) {
                        this.map = map;
                        const container = document.createElement('div');
                        container.className = 'mapboxgl-ctrl mapboxgl-ctrl-group';
                        container.appendChild(this.button);
                        return container;
                    }
                    onRemove() {
                        this.button.removeEventListener('click', this.onClick);
                        this.button.remove();
                    }
                }
                const customSearchButton = new CustomSearchButton();
                map.addControl(customSearchButton, 'top-right');

                // CUSTOM POI FILTER BUTTON
                class CustomFilterButton {
                    constructor() {
                        this.button = document.createElement('button');
                        this.button.className = 'mapbox-custom-button';
                        this.button.innerHTML = '<i class="material-icons" style="font-size: 32px;">filter_list</i>';
                        this.button.title = "Toggle POIs";

                        this.button.style.backgroundColor = '#fff';
                        this.button.style.color = '#000';
                        this.button.style.border = 'none';
                        this.button.style.borderRadius = '4px';
                        this.button.style.padding = '0';
                        this.button.style.cursor = 'pointer';
                        this.button.style.margin = '6px';

                        this.button.addEventListener('click', () => {
                            this.showPOIFilter();
                        });
                    }

                    onAdd(map) {
                        this.map = map;
                        const container = document.createElement('div');
                        container.className = 'mapboxgl-ctrl mapboxgl-ctrl-group';
                        container.appendChild(this.button);
                        return container;
                    }

                    onRemove() {
                        this.button.removeEventListener('click', this.onClick);
                        this.button.remove();
                    }

                    showPOIFilter() {
                        const sheetHTML = `
                            <div class="sheet-modal">
                                <div class="toolbar">
                                    <div class="toolbar-inner justify-content-flex-end">
                                        <a class="link sheet-close">` + that.$t('planning.sheet.filter.close') + `</a>
                                    </div>
                                </div>
                                <div class="sheet-modal-inner">
                                    <div class="page-content">
                                        <div class="block">
                                            <div class="block-title">` + that.$t('planning.sheet.filter.title') + `</div>
                                            <div class="list list-strong list-dividers-ios">
                                                <ul>
                                                    <li>
                                                        <label class="item-checkbox item-checkbox-icon-start item-content">
                                                            <input type="checkbox" id="poi-restaurants">
                                                            <i class="icon icon-checkbox"></i>
                                                            <div class="item-inner">
                                                                <div class="item-title">` + that.$t('planning.sheet.filter.poi-restaurants') + `</div>
                                                            </div>
                                                        </label>
                                                    </li>
                                                    <li>
                                                        <label class="item-checkbox item-checkbox-icon-start item-content">
                                                            <input type="checkbox" id="poi-bus-stops">
                                                            <i class="icon icon-checkbox"></i>
                                                            <div class="item-inner">
                                                                <div class="item-title">` + that.$t('planning.sheet.filter.poi-bus-stops') + `</div>
                                                            </div>
                                                        </label>
                                                    </li>
                                                    <li>
                                                        <label class="item-checkbox item-checkbox-icon-start item-content">
                                                            <input type="checkbox" id="poi-favorites">
                                                            <i class="icon icon-checkbox"></i>
                                                            <div class="item-inner">
                                                                <div class="item-title">` + that.$t('planning.sheet.filter.favorites') + `</div>
                                                            </div>
                                                        </label>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>`;

                            f7.sheet.create({
                                content: sheetHTML,
                                backdrop: true,
                                on: {
                                    open: () => {
                                        const restaurantsCheckbox = document.querySelector('#poi-restaurants');
                                        const busStopsCheckbox = document.querySelector('#poi-bus-stops');
                                        const favoritesCheckbox = document.querySelector('#poi-favorites');

                                        restaurantsCheckbox.checked = that.showRestaurants;
                                        busStopsCheckbox.checked = that.showBusStops;
                                        favoritesCheckbox.checked = that.showFavorites;

                                        restaurantsCheckbox.addEventListener('change', (e) => {
                                            that.showAllPOIs = false;
                                            that.showRestaurants = e.target.checked;
                                            that.togglePOIs('poi-label', e.target.checked);
                                        });

                                        busStopsCheckbox.addEventListener('change', (e) => {
                                            that.showAllPOIs = false;
                                            that.showBusStops = e.target.checked;
                                            that.togglePOIs('transit-label', e.target.checked);
                                        });

                                        favoritesCheckbox.addEventListener('change', (e) => {
                                            that.showAllPOIs = false;
                                            that.showFavorites = e.target.checked;
                                            that.toggleFavorites(e.target.checked);
                                        });
                                    },
                                    close: () => {
                                        that.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                                    }
                                },
                            }).open();
                            that.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                    }
                }
                const customFilterButton = new CustomFilterButton();
                map.addControl(customFilterButton, 'top-right');

                this.map = map;
                map.on('load', (e) => {
                    this.disableMap();
                    this.updateCenterPosition();
                    this.reloadPOIState();

                    this.showToastWait(this.$t('planning.toast.geolocate'));
                    this.geoLocator.trigger();
                    this.map.resize();

                    const geoLocateControlButton = document.querySelector('.mapboxgl-ctrl-geolocate');
                    geoLocateControlButton.addEventListener('click', () => {
                        this.showToastWait(this.$t('planning.toast.geolocate'));
                        this.geoLocator.trigger();
                    });

                    this.addFavoritesToMap();

                    // const layers = map.getStyle().layers;
                    // console.log("Available layers:", layers);
                });

                this.map.on('movestart', () => {
                    this.isDragging = true;
                });

                this.map.on('moveend', () => {
                    this.isDragging = false;
                    this.updateCenterPosition();
                });

                // EVENT HANDLER FOR EVENTS TO ADD FAVORITES BY LONG PRESS
                // TODO: This is not working as expected, we need to find a better solution for this
                // const handlePressStart = (e) => {
                //     this.isDragging = false;
                    
                //     this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                //     this.longPressTimer = setTimeout(() => {
                //         if (!this.isDragging && !this.isPinching) {
                //             const coordinates = e.lngLat || e.touches[0].lngLat;
                //             this.addFavoriteMarker(coordinates);
                //         }
                //         clearTimeout(this.longPressTimer);
                //     }, this.longPressTime);
                    
                // };
                // const handlePressEnd = () => {
                //     clearTimeout(this.longPressTimer);
                // };

                // REPOSITION THE USERS LOCATION
                this.geoLocator.on('geolocate', async (position) => {
                    this.closeToastWait();
                    this.enableMap();

                    this.geoLocation = position.coords;
                    const { longitude, latitude } = position.coords;

                    const offsetLng = longitude;
                    const offsetLat = latitude;

                    this.userAddress = await this.getAddressFromCoordinates({ lat: latitude, lng: longitude });

                    map.flyTo({
                        center: [offsetLng, offsetLat],
                        zoom: map.getZoom(),
                        essential: true,
                    });

                    // ADD MOUSE EVENTS FOR ADDING FAVORITE MARKER
                    // TODO: Belongs to adding favorites by long press (needs rework!)
                    // this.map.on('mousedown', handlePressStart);
                    // this.map.on('mouseup', handlePressEnd);
                    // this.map.on('mouseleave', handlePressEnd);

                     // ADD TOUCH EVENTS FOR ADDING FAVORITE MARKER
                     // TODO: Belongs to adding favorites by long press (needs rework!)
                    // map.on('touchstart', (e) => {
                    //     if (e.originalEvent.touches.length > 1) {
                    //         that.isPinching = true;
                    //         handlePressEnd();
                    //     } else {
                    //         handlePressStart(e);
                    //     }
                    // });

                    // map.on('touchmove', (e) => {
                    //     if (that.isPinching) {
                    //         handlePressEnd();
                    //     }
                    // });

                    // map.on('touchend', (e) => {
                    //     if (that.isPinching) {
                    //         that.isPinching = false;
                    //     } else {
                    //         handlePressEnd();
                    //     }
                    // });
                });

                this.geoLocator.on('error', async (position) => {
                    that.sendHapticFeedback('REJECT', 'Error');
                    this.mapDisabledText = this.$t('planning.map-not-available');
                    this.mapSettingsButton = true;
                    this.closeToastWait();
                });

                // MAKE POIs CLICKABLE
                map.on('style.load', function() {
                    map.on('click', (e) => {
                        if (that.isEditFavoritesMode) return;
                        if (!that.geoLocation) return;

                        var features = map.queryRenderedFeatures(e.point, { layers: ['poi-label', 'transit-label'] });

                        if (features.length > 0) {
                            let name = features[0].properties.name ? features[0].properties.name : '';

                            const destination = {
                                destLatitude: e.lngLat.lat,
                                destLongitude: e.lngLat.lng,
                                destPlaceName: name,
                                userPlaceName: that.userAddress,
                                geoLocation: that.geoLocation
                            };
                            that.$emit('marker-clicked', destination);
                        }
                    });
                });
            })
        },
        methods: {
            mapReload() {
                f7.view.current.router.refreshPage();
                this.showToastWait(this.$t('planning.toast.geolocate'));
                this.geoLocator.trigger();
            },
            goToSettings() {
                if (this.device.cordova) {
                    f7.dialog.alert(this.$t('planning.map-reload-hint'), this.$t('app.dialog.hint.title'));
                    this.diagnostic.switchToSettings(function(){
                        console.log("Successfully switched to Settings app");
                    }, function(error){
                        console.error("The following error occurred: " + error);
                    });
                }
            },
            disableMap() {
                this.mapOverlayEnabled = true;
                this.mapSettingsButton = true;
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
                this.mapSettingsButton = false;
            },
            updateCenterPosition() {
                const center = this.map.getCenter();
                this.mapCenter = { lng: center.lng, lat: center.lat };
            },
            reloadPOIState() {
                this.togglePOIs('poi-label', this.showRestaurants);
                this.togglePOIs('transit-label', this.showBusStops);
                this.toggleFavorites(this.showFavorites);
            },
            togglePOIs(layer, isVisible) {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                const visibility = isVisible ? 'visible' : 'none';
                this.map.setLayoutProperty(layer, 'visibility', visibility);
            },
            toggleFavorites(isVisible) {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                if (!isVisible) {
                    this.clearFavoriteMarkers();
                } else {
                    this.addFavoritesToMap();
                }
            },
            async getLocalPOIs(lat, long, query, limit) {
                try {
                    console.log("FETCHING POIs...");
                    const response = await poiService.poiSearch(lat, long, query, limit);
                    if (response.status === 200) {
                        this.addPOIsToMap(response.data.pois);
                        return response.data.pois;
                    } else {
                        return [];
                    }
                } catch(err) {
                    console.log("ERROR FETCHING POIs: ", err)
                    return [];
                }
            },
            addPOIsToMap(pois) {
                try {
                    this.clearMarkers();
                    pois.forEach(poi => {
                        const marker = new mapboxgl.Marker()
                            .setLngLat([poi.longitude, poi.latitude])
                            .addTo(this.map);

                        const popupOffsets = {
                            'top': [0, 0],
                            'bottom': [0, -30]
                        };

                        const popup = new mapboxgl.Popup({closeButton: false, offset: popupOffsets})
                            .setHTML(`${poi.name}`)
                            .addTo(this.map);

                        marker.setPopup(popup);

                        this.markers.push(marker);

                        marker.getElement().addEventListener('click', () => {
                            
                            const destination = {
                                destLatitude: poi.latitude,
                                destLongitude: poi.longitude,
                                destPlaceName: poi.name,
                                userPlaceName: this.userAddress,
                                geoLocation: this.geoLocation
                            };
                            this.$emit('marker-clicked', destination);
                        });
                    });
                } catch (err) {
                    console.log("ERROR ADDING POIs: ", err)
                }
            },
            // Adding the existing favorites as markers to the map instance
            addFavoritesToMap() {
                if (!this.favorites) return;
                if (!this.showFavorites) return;

                this.clearFavoriteMarkers();

                this.favorites.forEach(favorite => {
                    let markerIcon = 'fa-solid fa-map-pin';
                    if(favorite.icon === "f7:house") { markerIcon = 'fa-solid fa-house' };
                    if(favorite.icon === "f7:bag") { markerIcon = 'fa-solid fa-briefcase' };

                    const markerEl = document.createElement('div');
                    const markerInner = document.createElement('div');
                    markerInner.className = 'marker';
                    markerEl.appendChild(markerInner);

                    const marker = new FontawesomeMarker({
                        id: 'favorite-marker',
                        draggable: this.isEditFavoritesMode,
                        icon: markerIcon,
                        iconColor: '#fff',
                        color: '#99aa00',
                        scale: 1.5
                    })
                        .setLngLat([favorite.long, favorite.lat])
                        .addTo(this.map);

                    const popupOffsets = {
                        'top': [0, 0],
                        'bottom': [0, -50]
                    };

                    const popup = new mapboxgl.Popup({closeButton: false, offset: popupOffsets})
                        .setHTML(`${favorite.type}`)
                        .addTo(this.map);

                    marker.setPopup(popup);
                    // marker.addClassName('favorite-marker');

                    this.favoritesMarker.push(marker);

                    marker.on('dragstart', () => {
                        if (!this.isEditFavoritesMode) return;
                        console.log("MARKER DRAG START...")
                        this.isDragging = true;
                        this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
                        this.emitter.emit('close-last-destinations', '');
                        const trashBin = document.getElementById('trash-bin');
                        trashBin.style.display = 'flex';
                    });

                    marker.on('dragend', async () => {
                        if (!this.isEditFavoritesMode) return;
                        console.log("MARKER DRAG END...")
                        this.isDragging = false;
                        const lngLat = marker.getLngLat();
                        var address = await this.getAddressFromCoordinates(lngLat);
                        const trashBin = document.getElementById('trash-bin');
                        const trashBinRect = trashBin.getBoundingClientRect();

                        const markerElement = marker.getElement();
                        const markerRect = markerElement.getBoundingClientRect();

                        const isOverTrashBin = (
                            markerRect.bottom >= trashBinRect.top && 
                            markerRect.top <= trashBinRect.bottom && 
                            markerRect.right >= trashBinRect.left && 
                            markerRect.left <= trashBinRect.right
                        );
                        
                        if (isOverTrashBin) {
                            this.deleteFavorite(favorite.id);
                            marker.remove();
                        } else {
                            this.updateFavorite(favorite.id, lngLat, address);
                        }
                        trashBin.style.display = 'none';
                        trashBin.style.width = '50px';
                        trashBin.style.height = '50px';
                        markerElement.style.zIndex = '';

                        this.emitter.emit('open-last-destinations', '');
                    });

                    marker.on('drag', () => {
                        if (!this.isEditFavoritesMode) return;
                        const trashBin = document.getElementById('trash-bin');
                        const trashIcon = document.getElementById('trash-icon');
                        const markerElement = marker.getElement();
                        const markerRect = markerElement.getBoundingClientRect();
                        
                        const trashBinRect = trashBin.getBoundingClientRect();
                        const isOverTrashBin = (
                            markerRect.bottom >= trashBinRect.top && 
                            markerRect.top <= trashBinRect.bottom && 
                            markerRect.right >= trashBinRect.left && 
                            markerRect.left <= trashBinRect.right
                        );

                        if (isOverTrashBin) {
                            trashIcon.style.fontSize = '32px';
                            trashBin.style.background = `rgba(255, 0, 0, 0.50)`;
                            trashBin.style.borderRadius = '35px'; 
                            trashBin.style.width = '70px';
                            trashBin.style.height = '70px';
                            markerElement.style.zIndex = '10';
                        } else {
                            trashIcon.style.fontSize = '26px';
                            trashBin.style.background = `rgba(0, 119, 255, 0.5)`;
                            trashBin.style.borderRadius = '25px'; 
                            trashBin.style.width = '50px';
                            trashBin.style.height = '50px';
                            markerElement.style.zIndex = '';
                        }
                    });

                    if (!this.isEditFavoritesMode) {
                        marker.getElement().addEventListener('click', (event) => {
                            event.stopPropagation();

                            const destination = {
                                id: favorite.id,
                                name: favorite.type,
                                destLatitude: favorite.lat,
                                destLongitude: favorite.long,
                                destPlaceName: favorite.address,
                                userPlaceName: this.userAddress,
                                geoLocation: this.geoLocation
                            };
                            if (favorite.rideOption != null) {
                                this.$emit('marker-clicked-for-popover', {
                                    destination: destination,
                                    rideOption: favorite.rideOption,
                                    targetElement: event.currentTarget
                                });
                            } else {
                                this.$emit('marker-clicked', destination);
                            }
                        });
                    }
                });
            },
            // Add a new favorite to the map instance
            async addFavoriteMarker(coordinates) {
                this.emitter.emit('close-last-destinations', '');
                const marker = new mapboxgl.Marker({
                    id: 'favorite-marker',
                    draggable: this.isEditFavoritesMode,
                    color: "#99aa00",
                    scale: 1.5
                })
                    .setLngLat([coordinates.lng, coordinates.lat])
                    .addTo(this.map);
                
                var address = await this.getAddressFromCoordinates(coordinates);

                let newFavorite = await this.addFavorite(coordinates, address, marker);

                const popupOffsets = {
                    'top': [0, 0],
                    'bottom': [0, -50]
                };

                const popup = new mapboxgl.Popup({closeButton: false, offset: popupOffsets})
                .setHTML(`${newFavorite.type}`)
                .addTo(this.map);

                marker.setPopup(popup);

                this.favoritesMarker.push(marker);

                marker.on('dragstart', () => {
                    this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                    this.emitter.emit('close-last-destinations', '');
                    this.isDragging = true;
                    const trashBin = document.getElementById('trash-bin');
                    trashBin.style.display = 'flex';
                });

                marker.on('dragend', () => {
                    this.isDragging = false;
                    const lngLat = marker.getLngLat();
                    const trashBin = document.getElementById('trash-bin');
                    const trashBinRect = trashBin.getBoundingClientRect();
                    
                    const markerElement = marker.getElement();
                    const markerRect = markerElement.getBoundingClientRect();

                    const isOverTrashBin = (
                        markerRect.bottom >= trashBinRect.top && 
                        markerRect.top <= trashBinRect.bottom && 
                        markerRect.right >= trashBinRect.left && 
                        markerRect.left <= trashBinRect.right
                    );
                    
                    if (isOverTrashBin) {
                        this.deleteFavorite(newFavorite.id);
                        marker.remove();
                    } else {
                        this.updateFavorite(newFavorite.id, lngLat, address);
                    }
                    trashBin.style.display = 'none';
                    trashBin.style.width = '50px';
                    trashBin.style.height = '50px';
                    markerElement.style.zIndex = '';

                    this.emitter.emit('open-last-destinations', '');
                });

                marker.on('drag', () => {
                    const trashBin = document.getElementById('trash-bin');
                    const trashIcon = document.getElementById('trash-icon');
                    const markerElement = marker.getElement();
                    const markerRect = markerElement.getBoundingClientRect();
                    
                    const trashBinRect = trashBin.getBoundingClientRect();
                    const isOverTrashBin = (
                        markerRect.bottom >= trashBinRect.top && 
                        markerRect.top <= trashBinRect.bottom && 
                        markerRect.right >= trashBinRect.left && 
                        markerRect.left <= trashBinRect.right
                    );

                    if (isOverTrashBin) {
                        trashIcon.style.fontSize = '32px';
                        trashBin.style.background = `rgba(255, 0, 0, 0.50)`; 
                        trashBin.style.borderRadius = '35px'; 
                        trashBin.style.width = '70px';
                        trashBin.style.height = '70px';
                        markerElement.style.zIndex = '10';
                    } else {
                        trashIcon.style.fontSize = '26px';
                        trashBin.style.background = `rgba(0, 119, 255, 0.5)`;
                        trashBin.style.borderRadius = '25px';
                        trashBin.style.width = '50px';
                        trashBin.style.height = '50px';
                        markerElement.style.zIndex = '';
                    }
                });

                marker.getElement().addEventListener('click', (event) => {
                    event.stopPropagation();

                    const destination = {
                        destLatitude: coordinates.lat,
                        destLongitude: coordinates.lng,
                        destPlaceName: address,
                        userPlaceName: this.userAddress,
                        geoLocation: this.geoLocation
                    };
                    this.$emit('marker-clicked', destination);
                });
            },
            async addFavorite(coordinates, address, marker) {
                return new Promise((resolve, reject) => {
                    var maxId = this.favorites.reduce((max, entry) => Math.max(max, entry.id), 0);
                    var newID = maxId + 1;

                    f7.dialog.prompt("Name this Favorite", (type) => {
                        if (type == '') { marker.remove(); return; }

                        let newFavorite = {
                            id: newID,
                            address: address,
                            icon: 'f7:map_pin_ellipse',
                            lat: coordinates.lat,
                            long: coordinates.lng,
                            type: type
                        }
                        this.favorites.push(newFavorite);

                        this.sendHapticFeedback('CONFIRM', 'Success');
                        this.$store.dispatch('setFavorites', { favorites: this.favorites });

                        resolve({ id: newID, type: type });
                    }, () => {
                        marker.remove();
                        this.emitter.emit('open-last-destinations', '');
                        reject('Prompt canceled');
                    });
                });
            },
            deleteFavorite(favoriteId) {
                this.sendHapticFeedback('CONFIRM', 'Success');
                this.$store.dispatch('deleteFavorite', { id: favoriteId });
            },
            updateFavorite(favoriteId, coordinates, address) {
                this.sendHapticFeedback('CONFIRM', 'Success');
                this.$store.dispatch('updateFavoriteCoordinates', { id: favoriteId, lat: coordinates.lat, lng: coordinates.lng, address: address });
            },
            async getAddressFromCoordinates(coordinates) {
                try {
                    const response = await fetch(`${this.mapboxAPI}${this.mapboxPlacesURI}${coordinates.lng},${coordinates.lat}.json?access_token=${this.accessToken}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    const data = await response.json();
                    const address = data.features[0]?.place_name;
                    return address || 'Adresse nicht gefunden';
                } catch (error) {
                    console.error('Fehler beim Abrufen der Adresse:', error);
                    return 'Fehler beim Abrufen der Adresse';
                }
            },
            async handleSearch(query) {
                try {
                    this.clearMarkers();

                    if (!query) return;
                    
                    // v5 API URL
                    const response = await fetch(`${this.mapboxAPI}${this.mapboxPlacesURI}${encodeURIComponent(query)}.json?country=${this.countryCode}&access_token=${this.accessToken}&limit=${this.searchLimit}`);
                    const localPois = await this.getLocalPOIs(this.mapCenter.lat, this.mapCenter.lng, encodeURIComponent(query), this.poiLimit);

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const data = await response.json();
                    const mapboxResults = data.features || [];

                    const standardizedMapboxResults = mapboxResults.map(feature => ({
                        name: feature.place_name || '',
                        coordinates: feature.geometry.coordinates,
                        lat: feature.geometry.coordinates[1],
                        long: feature.geometry.coordinates[0],
                        placeType: feature.place_type[0],
                    }));

                    const standardizedLocalPois = localPois.map(poi => {
                        const address = [
                            poi.osm_data.street ?? '',
                            poi.osm_data.housenumber ?? '',
                            poi.osm_data.postcode ?? '',
                            poi.osm_data.district ?? ''
                        ].filter(Boolean).join(' ');

                        return {
                            name: poi.name + ' ' + address.trim(),
                            coordinates: [poi.longitude, poi.latitude],
                            lat: poi.latitude,
                            long: poi.longitude,
                            placeType: poi.osm_data.osm_value
                        };
                    });

                    const combinedResults = [...standardizedLocalPois, ...standardizedMapboxResults];

                    this.$emit('update-search-results', combinedResults);
                } catch (error) {
                    console.error('Error during search:', error);
                }
            },
            async handlePickResult(result) {
                try {
                    console.log("CLICK RESULT: ",result)
                    this.clearMarkers();

                    if (!result) return;

                    const marker = new mapboxgl.Marker()
                        .setLngLat([result.long, result.lat])
                        .addTo(this.map);

                    this.markers.push(marker);

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

                    marker.getElement().addEventListener('click', (event) => {
                        event.stopPropagation();
                        const destination = {
                            destLatitude: result.lat,
                            destLongitude: result.long,
                            destPlaceName: result.name,
                            destPlaceType: result.placeType,
                            userPlaceName: this.userAddress,
                            geoLocation: this.geoLocation
                        };
                        this.$emit('marker-clicked', destination);
                    });

                    popup.getElement().addEventListener('click', (event) => {
                        event.stopPropagation();
                        const destination = {
                            destLatitude: result.lat,
                            destLongitude: result.long,
                            destPlaceName: result.name,
                            destPlaceType: result.placeType,
                            userPlaceName: this.userAddress,
                            geoLocation: this.geoLocation
                        };
                        this.$emit('marker-clicked', destination);
                    });

                    this.map.flyTo({ 
                        center: [result.long, result.lat], 
                        zoom: 14,
                        offset: [0, 0],
                        speed: 2,
                        curve: 1.5,
                    });
                } catch (error) {
                    console.error('ERROR: ', error);
                }
            },
            async handlePickFavorite(favorite) {
                try {
                    console.log("CLICK RESULT FAVORITE: ",favorite)
                    this.clearMarkers();

                    if (!favorite) return;

                    this.map.flyTo({ 
                        center: [favorite.long, favorite.lat], 
                        zoom: 14,
                        offset: [0, 0],
                        speed: 2,
                        curve: 1.5,
                    });
                } catch (error) {
                    console.error('ERROR: ', error);
                }
            },
            async handlePickLastDestination(lastDestination) {
                try {
                    console.log("CLICK RESULT LAST DESTINATION: ",lastDestination)

                    this.clearMarkers();
                    if (!lastDestination) return;

                    const marker = new mapboxgl.Marker()
                        .setLngLat([lastDestination.long, lastDestination.lat])
                        .addTo(this.map);

                    this.markers.push(marker);

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
                                ${lastDestination.address}
                            </div>`)
                        .setLngLat([lastDestination.long, lastDestination.lat])
                        .addTo(this.map);

                    marker.setPopup(popup);

                    marker.getElement().addEventListener('click', (event) => {
                        event.stopPropagation();
                        const destination = {
                            destLatitude: lastDestination.lat,
                            destLongitude: lastDestination.long,
                            destPlaceName: lastDestination.address,
                            destPlaceType: lastDestination.type,
                            userPlaceName: this.userAddress,
                            geoLocation: this.geoLocation
                        };
                        this.$emit('marker-clicked', destination);
                    });

                    popup.getElement().addEventListener('click', (event) => {
                        event.stopPropagation();
                        const destination = {
                            destLatitude: lastDestination.lat,
                            destLongitude: lastDestination.long,
                            destPlaceName: lastDestination.address,
                            destPlaceType: lastDestination.type,
                            userPlaceName: this.userAddress,
                            geoLocation: this.geoLocation
                        };
                        this.$emit('marker-clicked', destination);
                    });

                    this.map.flyTo({ 
                        center: [lastDestination.long, lastDestination.lat], 
                        zoom: 14,
                        offset: [0, 0],
                        speed: 2,
                        curve: 1.5,
                    });
                } catch (error) {
                    console.error('ERROR: ', error);
                }
            },
            clearMarkers() {
                this.markers.forEach(marker => marker.remove());
                this.markers = [];
            },
            clearFavoriteMarkers() {
                this.favoritesMarker.forEach(marker => marker.remove());
                this.favoritesMarker = [];
            },
            updateSearchResults(results) {
                this.searchResults = results;
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
            this.mapOverlayEnabled = true;
            this.mapSettingsButton = false;
            this.mapDisabledText = '';
            this.geoLocator = null;
            this.geoLocation = null;
        }
    };
</script>
<style scoped>
    .edit-favorites-toast {
        background: #99aa00 !important;
        color: white !important;
        font-weight: bold;
    }
    #trash-bin {
        transition: background-color 0.4s;
        position: fixed; 
        bottom: 90px; 
        left: 50%; 
        transform: translateX(-50%); 
        width: 50px; 
        height: 50px; 
        background: rgba(0, 119, 255, 0.5); 
        border-radius: 25px; 
        display: none; 
        justify-content: center; 
        text-align: center;
        align-items: center;
        z-index: 1;
    }
    #trash-bin.active {
        display: flex;
        background-color: darkred;
    }

    .map-overlay {
        transition: background-color 1.0s;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(128, 128, 128, 0.7);
        color: rgba(255, 255, 255, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 20px;
        font-size: 24px;
        line-height: 1.3em;
        z-index: 10;
    }
    .map-overlay-link {
        padding: 20px;
    }
    .map-container {
        height: calc(100% - var(--f7-toolbar-height));
        width: 100% !important;
    }
    :deep(.mapboxgl-ctrl-geolocate) {
        width: 40px !important;
        height: 40px !important;
        font-size: 24px !important;
    }
    :deep(.search-location-popup .mapboxgl-popup-close-button) {
        display: none !important;
    }
    :deep(.search-location-popup-text) {
        text-align: center;
    }
    :deep(.mapboxgl-popup-content) {
        color: black !important;
    }
</style>