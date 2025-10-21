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

export const v275 = {
  version: 275,
  up: state => {
    console.log('Running migration 275, initial state:', state);

    // REMOVE OLD DATA
    const newSettings = { ...state.appSettings.settings };
    if (newSettings.hasOwnProperty('app_version')) {
      delete newSettings['app_version'];
    }
    if (newSettings.hasOwnProperty('fast_start_options')) {
      delete newSettings['fast_start_options'];
    }

    // ADD NEW DATA
    const newState = {
      ...state,
      appSettings: {
        ...state.appSettings,
        settings: {
          ...state.appSettings.settings,
          app_version: AppSettingsData.APP_VERSION,
          fast_start_options: AppSettingsData.FAST_START_OPTIONS,
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
    console.log('Migration 275 result:', newState);
    return newState;
  }
};