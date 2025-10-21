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

// Import Vue
import { createApp } from 'vue';

// Import Framework7
import Framework7 from 'framework7/bundle';

// Import Framework7-Vue Plugin
import Framework7Vue, { registerComponents } from 'framework7-vue/bundle';

// Import Framework7 Styles
import 'framework7/css/bundle';

// Import Icons and App Custom Styles
import '../css/icons.css';
import '../css/all.css';
import '../css/app.css';

// Import App Component
import App from '../components/app.vue';

// Import other plugins
import Vuex from 'vuex';
import { i18n } from '../locales/i18n';
import { store } from '../vuex/store';

import axios from 'axios';

import mitt from 'mitt';
const emitter = mitt();

// Init axios
const axiosInstance = axios.create({})
// axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${store.getters.getUserToken}`;

// Init Framework7-Vue Plugin
Framework7.use(Framework7Vue);

// Init App
const app = createApp(App);

// Register Framework7 Vue components
registerComponents(app);

// Register other plugins with app
app.config.globalProperties.axios = { ...axiosInstance }
app.config.globalProperties.emitter = { ...emitter }

app.use(Vuex);
app.use(i18n);
app.use(store);
app.use(emitter);

// Mount the app
app.mount('#app');