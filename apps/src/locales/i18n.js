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

// Import vuex store
import { store } from '@/vuex/store';

// Import vue-i18n localisation package
import { createI18n } from 'vue-i18n'

// Import localisations (languages) from index.js
import { languages } from '@/locales/index.js';

// Localisation Setup
const messages = Object.assign(languages);

var initialLocale = 'de';
if (store.getters.getAppLanguage) { initialLocale = store.getters.getAppLanguage }

export const i18n = createI18n({
  locale: initialLocale,
  fallbackLocale: 'de',
  messages
});