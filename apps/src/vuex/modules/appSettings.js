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

import { AppSettingsData } from "@/data/appSettingsData";
import { AppUserDefaultPrefs } from "@/data/appUserDefaultPrefs";
import systemService from '@/services/systemService';

const apiHost = AppUserDefaultPrefs.DEV_MODE 
    ? AppSettingsData.API_HOSTS.development 
    : AppSettingsData.API_HOSTS.production;

// App Settings Setup
export const appSettings = {
    state: () => ({
        settings: {
            app_version: null,

            api_host: null,
            api_url: null,
            api_image_url: null,

            fast_start_options: null,

            push_token: null,

            home_badge_count: 0,
            planning_badge_count: 0,
            activity_badge_count: 0,
            account_badge_count: 0,
            wallet_badge_count: 0,
            prefs_badge_count: 0,

            mapbox_api: null,
            mapbox_token: null,
            mapbox_driving_uri: null,
            mapbox_walking_uri: null,
            mapbox_cycling_uri: null,
            mapbox_places_uri: null,
            mapbox_style: null,
            mapbox_bbox_coords: null,

            pooling_download_url: null,
            pooling_register: null,
            pooling_planned_driver: null,
            pooling_previous_driver: null,
            pooling_planned_passenger: null,
            pooling_previous_passenger: null,
            pooling_ride_offer: null,
            pooling_is_linked: false,
            pooling_authkey: null,

            showRestaurants: true,
            showBusStops: true,
            showFavorites: true,

            plugin_geolocation: null,
            plugin_haptic: null,
            plugin_device: null,
            plugin_diagnostic: null,
            plugin_inAppBrowser: null,
            plugin_camera: null,
            plugin_file: null,
            plugin_fileTransfer: null,
            plugin_fileUploadOptions: null,

            faceid_login: null,
            language: null,
            localeString: null,
            store_destinations: null,
            app_mode: null,
            dev_mode: null,
            networkStatus: null,
            currentRoute: '/',
            statusBar: null
        },
        default: {
            settings: {
                app_version: AppSettingsData.APP_VERSION,

                api_host: apiHost,
                api_url: AppSettingsData.API_URL,
                api_image_url: AppSettingsData.API_IMAGE_URL,

                fast_start_options: null,

                push_token: null,

                home_badge_count: 0,
                planning_badge_count: 0,
                activity_badge_count: 0,
                account_badge_count: 0,
                wallet_badge_count: 0,
                prefs_badge_count: 0,

                mapbox_api: '',
                mapbox_token: '',
                mapbox_driving_uri: '',
                mapbox_walking_uri: '',
                mapbox_cycling_uri: '',
                mapbox_places_uri: '',
                mapbox_style: '',
                mapbox_bbox_coords: [],

                pooling_download_url: '',
                pooling_register: '',
                pooling_planned_driver: '',
                pooling_previous_driver: '',
                pooling_planned_passenger: '',
                pooling_previous_passenger: '',
                pooling_ride_offer: '',
                pooling_is_linked: false,
                pooling_authkey: null,

                showRestaurants: true,
                showBusStops: true,
                showFavorites: true,

                plugin_geolocation: null,
                plugin_haptic: null,
                plugin_device: null,
                plugin_diagnostic: null,
                plugin_inAppBrowser: null,
                plugin_camera: null,
                plugin_file: null,
                plugin_fileTransfer: null,
                plugin_fileUploadOptions: null,

                faceid_login: AppUserDefaultPrefs.FACEID_LOGIN,
                language: AppUserDefaultPrefs.LANGUAGE,
                localeString: AppUserDefaultPrefs.LOCALESTRING,
                store_destinations: AppUserDefaultPrefs.STORE_DESTINATIONS,
                app_mode: AppUserDefaultPrefs.APP_MODE,
                dev_mode: AppUserDefaultPrefs.DEV_MODE,
                networkStatus: null,
                currentRoute: '/',
                statusBar: null
            }
        }
    }),
    mutations: {
        SET_APP_SETTINGS: (state, settings) => {
            let poolingBaseUrl;
            for(const [key,value] of Object.entries(settings)) {
                if (["POOLING_DOWNLOAD_URLS"].includes(key)) {
                    state.settings.pooling_download_url = state.settings.dev_mode 
                    ? settings[key].development 
                    : settings[key].production;
                } else if (["POOLING_URLS"].includes(key)) {
                    poolingBaseUrl = state.settings.dev_mode 
                    ? settings[key].development 
                    : settings[key].production;
                } else {
                    state.settings[key.toLowerCase()] = value;
                }
            }
            state.settings.pooling_register = poolingBaseUrl + state.settings.pooling_register;
            state.settings.pooling_planned_driver = poolingBaseUrl + state.settings.pooling_planned_driver;
            state.settings.pooling_previous_driver = poolingBaseUrl + state.settings.pooling_previous_driver;
            state.settings.pooling_planned_passenger = poolingBaseUrl + state.settings.pooling_planned_passenger;
            state.settings.pooling_previous_passenger = poolingBaseUrl + state.settings.pooling_previous_passenger;
            state.settings.pooling_ride_offer = poolingBaseUrl + state.settings.pooling_ride_offer;

            state.settings.api_host = state.settings.dev_mode  
            ? AppSettingsData.API_HOSTS.development 
            : AppSettingsData.API_HOSTS.production;
        },
        RESET_APP_SETTINGS: state => {
            Object.assign(state.settings, state.default.settings);
        },
        SET_API_HOST: (state, host) => {
            state.settings.api_host = host;
        },
        SET_API_URL: (state, url) => {
            state.settings.api_url = url;
        },
        SET_API_IMAGE_URL: (state, url) => {
            state.settings.api_image_url = url;
        },
        SET_PUSH_TOKEN: (state, token) => {
            state.settings.push_token = token;
        },
        SET_HOME_BADGE_COUNT: (state, count) => {
            state.settings.home_badge_count = count;
        },
        SET_PLANNING_BADGE_COUNT: (state, count) => {
            state.settings.planning_badge_count = count;
        },
        SET_ACTIVITY_BADGE_COUNT: (state, count) => {
            state.settings.activity_badge_count = count;
        },
        SET_ACCOUNT_BADGE_COUNT: (state, count) => {
            state.settings.account_badge_count = count;
        },
        SET_WALLET_BADGE_COUNT: (state, count) => {
            state.settings.wallet_badge_count = count;
        },
        SET_PREFS_BADGE_COUNT: (state, count) => {
            state.settings.prefs_badge_count = count;
        },

        SET_MAPBOX_API: (state, url) => {
            state.settings.mapbox_api = url;
        },
        SET_MAPBOX_TOKEN: (state, token) => {
            state.settings.mapbox_token = token;
        },
        SET_MAPBOX_DRIVING_URI: (state, uri) => {
            state.settings.mapbox_driving_uri = uri;
        },
        SET_MAPBOX_WALKING_URI: (state, uri) => {
            state.settings.mapbox_walking_uri = uri;
        },
        SET_MAPBOX_CYCLING_URI: (state, uri) => {
            state.settings.mapbox_cycling_uri = uri;
        },
        SET_MAPBOX_PLACES_URI: (state, uri) => {
            state.settings.mapbox_places_uri = uri;
        },
        SET_MAPBOX_STYLE: (state, style) => {
            state.settings.mapbox_style = style;
        },
        SET_MAPBOX_BBOX_COORDS: (state, cords) => {
            state.settings.mapbox_bbox_coords = cords;
        },

        SET_POOLING_DOWNLOAD_URL: (state, url) => {
            state.settings.pooling_download_url = url;
        },
        SET_POOLING_REGISTER: (state, url) => {
            state.settings.pooling_register = url;
        },
        SET_POOLING_PLANNED_DRIVER: (state, url) => {
            state.settings.pooling_planned_driver = url;
        },
        SET_POOLING_PREVIOUS_DRIVER: (state, url) => {
            state.settings.pooling_previous_driver = url;
        },
        SET_POOLING_PLANNED_PASSENGER: (state, url) => {
            state.settings.pooling_planned_passenger = url;
        },
        SET_POOLING_PREVIOUS_PASSENGER: (state, url) => {
            state.settings.pooling_previous_passenger = url;
        },
        SET_POOLING_RIDE_OFFER: (state, url) => {
            state.settings.pooling_ride_offer = url;
        },
        SET_POOLING_LINKED: (state, status) => {
            state.settings.pooling_is_linked = status;
        },
        SET_POOLING_AUTH_KEY: (state, key) => {
            state.settings.pooling_authkey = key;
        },

        SET_SHOW_RESTAURANTS: (state, value) => {
            state.settings.showRestaurants = value;
        },
        SET_SHOW_BUS_STOPS: (state, value) => {
            state.settings.showBusStops = value;
        },
        SET_SHOW_FAVORITES: (state, value) => {
            state.settings.showFavorites = value;
        },

        SET_PLUGIN_GEOLOCATION(state, pluginGeolocation) {
            state.settings.plugin_geolocation = pluginGeolocation;
        },
        SET_PLUGIN_HAPTIC(state, pluginHaptic) {
            state.settings.plugin_haptic = pluginHaptic;
        },
        SET_PLUGIN_DEVICE(state, pluginDevice) {
            state.settings.plugin_device = pluginDevice;
        },
        SET_PLUGIN_DIAGNOSTIC(state, pluginDiagnostic) {
            state.settings.plugin_diagnostic = pluginDiagnostic;
        },
        SET_PLUGIN_INAPP_BROWSER(state, pluginInAppBrowser) {
            state.settings.plugin_inAppBrowser = pluginInAppBrowser;
        },
        SET_PLUGIN_CAMERA(state, pluginCamera) {
            state.settings.plugin_camera = pluginCamera;
        },
        SET_PLUGIN_FILE(state, pluginFile) {
            state.settings.plugin_file = pluginFile;
        },
        SET_PLUGIN_FILE_TRANSFER(state, pluginFileTransfer) {
            state.settings.plugin_fileTransfer = pluginFileTransfer;
        },
        SET_PLUGIN_FILE_UPLOAD_OPTIONS(state, pluginFileUploadOptions) {
            state.settings.plugin_fileUploadOptions = pluginFileUploadOptions;
        },
        SET_FACEID_LOGIN(state, faceid) {
            state.settings.faceid_login = faceid;
        },
        SET_APP_LANGUAGE(state, language) {
            state.settings.language = language;
        },
        SET_APP_LOCALESTRING(state, localeString) {
            state.settings.localeString = localeString;
        },
        SET_STORE_DESTINATIONS(state, days) {
            state.settings.store_destinations = days;
        },
        SET_APP_MODE(state, mode) {
            state.settings.app_mode = mode;
        },
        SET_DEV_MODE: (state, devmode) => {
            state.settings.dev_mode = devmode;
        },
        SET_NETWORK_STATUS: (state, networkStatus) => {
            state.settings.networkStatus = networkStatus;
        },
        SET_CURRENT_ROUTE: (state, route) => {
            state.settings.currentRoute = route;
        },
        SET_STATUS_BAR: (state, statusBar) => {
            state.settings.statusBar = statusBar;
        },
    },
    actions: {
        setAppSettings: async ({ commit }) => {
            var remoteSettings = {};

            let result = await systemService.getConfig();
            if (result.data) {
                remoteSettings = result.data;
            } else {
                console.log("ERROR GETTING CONFIG!!!");
            }
            const combinedAppSettings = Object.assign({}, AppSettingsData, remoteSettings);
            commit('SET_APP_SETTINGS', combinedAppSettings);
        },
        resetAppSettings: ({ commit }) => {
            commit('RESET_APP_SETTINGS', '');
        },
        setApiHost: ({ commit }, { host }) => {
            commit('SET_API_HOST', host);
        },
        setApiUrl: ({ commit }, { url }) => {
            commit('SET_API_URL', url);
        },
        setApiImageUrl: ({ commit }, { url }) => {
            commit('SET_API_IMAGE_URL', url);
        },
        setPushToken: ({ commit }, { token }) => {
            commit('SET_PUSH_TOKEN', token);
        },
        setHomeBadgeCount: ({ commit }, { count }) => {
            commit('SET_HOME_BADGE_COUNT', count);
        },
        setPlanningBadgeCount: ({ commit }, { count }) => {
            commit('SET_PLANNING_BADGE_COUNT', count);
        },
        setActivityBadgeCount: ({ commit }, { count }) => {
            commit('SET_ACTIVITY_BADGE_COUNT', count);
        },
        setAccountBadgeCount: ({ commit }, { count }) => {
            commit('SET_ACCOUNT_BADGE_COUNT', count);
        },
        setWalletBadgeCount: ({ commit }, { count }) => {
            commit('SET_WALLET_BADGE_COUNT', count);
        },
        setPrefsBadgeCount: ({ commit }, { count }) => {
            commit('SET_PREFS_BADGE_COUNT', count);
        },

        setMapboxApi: ({ commit }, { url }) => {
            commit('SET_MAPBOX_API', url);
        },
        setMapboxToken: ({ commit }, { token }) => {
            commit('SET_MAPBOX_TOKEN', token);
        },
        setMapboxDrivingURI: ({ commit }, { uri }) => {
            commit('SET_MAPBOX_DRIVING_URI', uri);
        },
        setMapboxWalkingURI: ({ commit }, { uri }) => {
            commit('SET_MAPBOX_WALKING_URI', uri);
        },
        setMapboxCyclingURI: ({ commit }, { uri }) => {
            commit('SET_MAPBOX_CYCLING_URI', uri);
        },
        setMapboxPlacesURI: ({ commit }, { uri }) => {
            commit('SET_MAPBOX_PLACES_URI', uri);
        },
        setMapboxStyle: ({ commit }, { style }) => {
            commit('SET_MAPBOX_STYLE', style);
        },
        setMapboxBboxCoords: ({ commit }, { coords }) => {
            commit('SET_MAPBOX_BBOX_COORDS', coords);
        },

        setPoolingDownloadURL: ({ commit }, { url }) => {
            commit('SET_POOLING_DOWNLOAD_URL', url);
        },
        setPoolingRegisterURL: ({ commit }, { url }) => {
            commit('SET_POOLING_REGISTER', url);
        },
        setPoolingPlannedDriverURL: ({ commit }, { url }) => {
            commit('SET_POOLING_PLANNED_DRIVER', url);
        },
        setPoolingPreviousDriverURL: ({ commit }, { url }) => {
            commit('SET_POOLING_PREVIOUS_DRIVER', url);
        },
        setPoolingPlannedPassengerURL: ({ commit }, { url }) => {
            commit('SET_POOLING_PLANNED_PASSENGER', url);
        },
        setPoolingPreviousPassengerURL: ({ commit }, { url }) => {
            commit('SET_POOLING_PREVIOUS_PASSENGER', url);
        },
        setPoolingRideOfferURL: ({ commit }, { url }) => {
            commit('SET_POOLING_RIDE_OFFER', url);
        },
        setPoolingIsLinked: ({ commit }, { status }) => {
            commit('SET_POOLING_LINKED', status);
        },
        setPoolingAuthKey: ({ commit }, { key }) => {
            commit('SET_POOLING_AUTH_KEY', key);
        },

        setShowRestaurants({ commit }, value) {
            commit('SET_SHOW_RESTAURANTS', value);
        },
        setShowBusStops({ commit }, value) {
            commit('SET_SHOW_BUS_STOPS', value);
        },
        setShowFavorites({ commit }, value) {
            commit('SET_SHOW_FAVORITES', value);
        },

        setPluginGeolocation({ commit }, pluginGeolocation) {
            commit('SET_PLUGIN_GEOLOCATION', pluginGeolocation);
        },        
        setPluginHaptic({ commit }, pluginHaptic) {
            commit('SET_PLUGIN_HAPTIC', pluginHaptic);
        },
        setPluginDevice({ commit }, pluginDevice) {
            commit('SET_PLUGIN_DEVICE', pluginDevice);
        },
        setPluginDiagnostic({ commit }, pluginDiagnostic) {
            commit('SET_PLUGIN_DIAGNOSTIC', pluginDiagnostic);
        },
        setPluginInAppBrowser({ commit }, pluginInAppBrowser) {
            commit('SET_PLUGIN_INAPP_BROWSER', pluginInAppBrowser);
        },
        setPluginCamera({ commit }, pluginCamera) {
            commit('SET_PLUGIN_CAMERA', pluginCamera);
        },
        setPluginFile({ commit }, pluginFile) {
            commit('SET_PLUGIN_FILE', pluginFile);
        },
        setPluginFileTransfer({ commit }, pluginFileTransfer) {
            commit('SET_PLUGIN_FILE_TRANSFER', pluginFileTransfer);
        },
        setPluginFileUpoadOptions({ commit }, pluginFileUploadOptions) {
            commit('SET_PLUGIN_FILE_UPLOAD_OPTIONS', pluginFileUploadOptions);
        },
        setFaceIDLogin({ commit }, { faceid }) {
            commit('SET_FACEID_LOGIN', faceid);
        },
        setAppLanguage({ commit }, { language }) {
            if (language == 'de') {commit('SET_APP_LOCALESTRING', 'de-DE');}
            if (language == 'en') {commit('SET_APP_LOCALESTRING', 'en-EN');}
            commit('SET_APP_LANGUAGE', language);
        },
        setAppLocaleString({ commit }, { localeString }) {
            commit('SET_APP_LOCALESTRING', localeString);
        },
        setStoreDestinations({ commit }, { days }) {
            commit('SET_STORE_DESTINATIONS', days);
        },
        setAppMode({ commit }, { mode }) {
            commit('SET_APP_MODE', mode);
        },
        setDevMode: ({ commit }, { devmode }) => {
            commit('SET_DEV_MODE', devmode);
        },
        setNetworkStatus: ({ commit }, { networkStatus }) => {
            commit('SET_NETWORK_STATUS', networkStatus);
        },
        setCurrentRoute: ({ commit }, { route }) => {
            commit('SET_CURRENT_ROUTE', route);
        },
        setStatusBar: ({ commit }, statusBar) => {
            commit('SET_STATUS_BAR', statusBar);
        },
    },
    getters : {
        getApiHost: state => state.settings.api_host,
        getApiUrl: state => state.settings.api_url,
        getApiImageUrl: state => state.settings.api_image_url,

        getFastStartOptions: state => state.settings.fast_start_options,

        getPushToken: state => state.settings.push_token,

        getHomeBadgeCount: state => state.settings.home_badge_count,
        getPlanningBadgeCount: state => state.settings.planning_badge_count,
        getActivityBadgeCount: state => state.settings.activity_badge_count,
        getAccountBadgeCount: state => state.settings.account_badge_count,
        getWalletBadgeCount: state => state.settings.wallet_badge_count,
        getPrefsBadgeCount: state => state.settings.prefs_badge_count,

        getMapboxApi: state => state.settings.mapbox_api,
        getMapboxToken: state => state.settings.mapbox_token,
        getMapboxDrivingURI: state => state.settings.mapbox_driving_uri,
        getMapboxWalkingURI: state => state.settings.mapbox_walking_uri,
        getMapboxCyclingURI: state => state.settings.mapbox_cycling_uri,
        getMapboxPlacesURI: state => state.settings.mapbox_places_uri,
        getMapboxStyle: state => state.settings.mapbox_style,
        getMapboxBBoxCoords: state => state.settings.mapbox_bbox_coords,

        getPoolingDownloadURL: state => state.settings.pooling_download_url,
        getPoolingRegister: state => state.settings.pooling_register,
        getPoolingPlannedDriver: state => state.settings.pooling_planned_driver,
        getPoolingPreviousDriver: state => state.settings.pooling_previous_driver,
        getPoolingPlannedPassenger: state => state.settings.pooling_planned_passenger,
        getPoolingPreviousPassenger: state => state.settings.pooling_previous_passenger,
        getPoolingRideOffer: state => state.settings.pooling_ride_offer,
        getPoolingIsLinked: state => state.settings.pooling_is_linked,
        getPoolingAuthKey: state => state.settings.pooling_authkey,

        getShowRestaurants: state => state.settings.showRestaurants,
        getShowBusStops: state => state.settings.showBusStops,
        getShowFavorites: state => state.settings.showFavorites,

        getPluginGeolocation: state => state.settings.plugin_geolocation,
        getPluginHaptic: state => state.settings.plugin_haptic,
        getPluginDevice: state => state.settings.plugin_device,
        getPluginDiagnostic: state => state.settings.plugin_diagnostic,
        getPluginInAppBrowser: state => state.settings.plugin_inAppBrowser,
        getPluginCamera: state => state.settings.plugin_camera,
        getPluginFile: state => state.settings.plugin_file,
        getPluginFileTransfer: state => state.settings.plugin_fileTransfer,
        getPluginFileUploadOptions: state => state.settings.plugin_fileUploadOptions,

        getFaceIDLogin: state => state.settings.faceid_login,
        getAppLanguage: state => state.settings.language,
        getAppLocaleString: state => state.settings.localeString,
        getStoreDestinations: state => state.settings.store_destinations,
        getAppMode: state => state.settings.app_mode,
        getAppModeConverted(state) {
            switch(state.settings.app_mode) {
                case 'light':
                    return false;
                case 'dark':
                    return true;
                case 'system':
                    return 'auto';
                default:
                    return 'auto';
            }
        },
        getDevMode: state => state.settings.dev_mode,
        getNetworkStatus: state => state.settings.networkStatus,
        getCurrentRoute: state => state.settings.currentRoute,
        getStatusBar: state => state.settings.statusBar
    }
}