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

import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import createMigrate from 'vuex-persistedstate-migrate'
import { sortedMigrations } from './migrations'

// Importing all the custom VUEX modules
import { appSettings } from './modules/appSettings';
import { appData } from './modules/appData';
import { wallet } from './modules/wallet';
import { tours } from './modules/tours';
import { userData } from './modules/userData';

// Create a single persisted state instance with migration
const persistedState = createPersistedState({
  key: 'icl-store',
  paths: [
    'appSettings.settings',
    'appData.data',
    'wallet.data',
    'tours.data',
    'userData.data',
    'migration'
  ],
  getState: createMigrate(sortedMigrations, 'migration.version', {
    debug: true // Enable debug mode
  })
})

export const store = createStore({
  plugins: [persistedState],
  modules: {
    appSettings,
    appData,
    wallet,
    tours,
    userData
  },
  state: {
    migration: {
      version: 189 // Set to a version before our first migration
    }
  }
})