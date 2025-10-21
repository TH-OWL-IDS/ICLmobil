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

export const v200 = {
  version: 200,
  up: state => {
    console.log('Running migration 200, initial state:', state);

    // REMOVE OLD DATA
    const newSettings = { ...state.appSettings.settings };
    if (newSettings.hasOwnProperty('app_version')) {
      delete newSettings['app_version'];
    }
    if (newSettings.hasOwnProperty('pooling_register')) {
      delete newSettings['pooling_register'];
    }
    if (newSettings.hasOwnProperty('pooling_planned_driver')) {
      delete newSettings['pooling_planned_driver'];
    }
    if (newSettings.hasOwnProperty('pooling_previous_driver')) {
      delete newSettings['pooling_previous_driver'];
    }
    if (newSettings.hasOwnProperty('pooling_planned_passenger')) {
      delete newSettings['pooling_planned_passenger'];
    }
    if (newSettings.hasOwnProperty('pooling_previous_passenger')) {
      delete newSettings['pooling_previous_passenger'];
    }
    if (newSettings.hasOwnProperty('pooling_ride_offer')) {
      delete newSettings['pooling_ride_offer'];
    }
    if (newSettings.hasOwnProperty('pooling_download_url')) {
      delete newSettings['pooling_download_url'];
    }

    // ADD NEW DATA
    const poolingBaseUrl = AppSettingsData.DEV_MODE
      ? AppSettingsData.POOLING_URLS.development
      : AppSettingsData.POOLING_URLS.production;

    const apiHost = AppSettingsData.DEV_MODE 
      ? AppSettingsData.API_HOSTS.development 
      : AppSettingsData.API_HOSTS.production;

    const poolingDownloadURL = AppSettingsData.DEV_MODE 
      ? AppSettingsData.POOLING_DOWNLOAD_URLS.development 
      : AppSettingsData.POOLING_DOWNLOAD_URLS.production;
      
    const newState = {
      ...state,
      appSettings: {
        ...state.appSettings,
        settings: {
          ...state.appSettings.settings,
          app_version: AppSettingsData.APP_VERSION,
          api_host: apiHost,
          api_image_url: AppSettingsData.API_IMAGE_URL,
          dev_mode: AppSettingsData.DEV_MODE,
          pooling_download_url: poolingDownloadURL,
          pooling_register: poolingBaseUrl + AppSettingsData.POOLING_REGISTER,
          pooling_planned_driver: poolingBaseUrl + AppSettingsData.POOLING_PLANNED_DRIVER,
          pooling_previous_driver: poolingBaseUrl + AppSettingsData.POOLING_PREVIOUS_DRIVER,
          pooling_planned_passenger: poolingBaseUrl + AppSettingsData.POOLING_PLANNED_PASSENGER,
          pooling_previous_passenger: poolingBaseUrl + AppSettingsData.POOLING_PREVIOUS_PASSENGER,
          pooling_ride_offer: poolingBaseUrl + AppSettingsData.POOLING_RIDE_OFFER
        }
      },
      appData: {
        ...state.appData,
        // Add any migrations for appData here
      },
      wallet: {
        ...state.wallet,
        // Add any migrations for wallet here
      },
      tours: {
        ...state.tours,
        // Add any migrations for tours here
      },
      userData: {
        ...state.userData,
        // Add any migrations for userData here
      }
    };
    console.log('Migration 200 result:', newState);
    return newState;
  }
};