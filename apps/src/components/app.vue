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
  <f7-app v-bind="f7params">
    <f7-view main class="safe-areas light" :browserHistory="isCypressRunning()" style="--f7-theme-color: #96D35F" url="/">
      <verifyData/>
      <notificationDispatcher/>
      <tourGuide/>
    </f7-view>  
    <canvas ref="confettiContainer"
      style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 2147483647; /* Maximalwert, um ganz sicher zu gehen */
      "
    ></canvas>
  </f7-app>
</template>
<script>
  import { getDevice }  from 'framework7';
  import { f7, f7ready } from 'framework7-vue';
  import cordovaApp from '../js/cordova-app.js';
  import { store } from '@/vuex/store.js';
  import JSConfetti from 'js-confetti';

  import routes from '../js/routes.js';

  import verifyData from './verifyData.vue';
  import notificationDispatcher from './notificationDispatcher.vue';
  import tourGuide from './tourGuide.vue';
  import userService from '@/services/userService';

  export default {
    data() {
      return {
        jsConfetti: null
      };
    },
    components: {
      verifyData,
      notificationDispatcher,
      tourGuide
    },
    setup() {
      const device = getDevice();
      var theme = 'auto';

      if (device.macos) { theme = 'ios'; }

      // Framework7 Parameters
      const f7params = {
        root: '#app',                   // App root element
        id: 'de.iclowl.iclmobile',      // App bundle ID
        name: 'ICLMobile',              // App name
        theme: theme,                   // Automatic theme detection
        routes: routes,                 // App routes

        input: {
          scrollIntoViewOnFocus: device.cordova && !device.electron,
          scrollIntoViewCentered: device.cordova && !device.electron,
        },
        statusbar: {
          iosOverlaysWebView: true,
          androidOverlaysWebView: true,
        },
        view: {
          animate: false,
          routesBeforeEnter: async function(to, from, resolve, reject) {
            const router = to;
            store.dispatch('setCurrentRoute', { route: router.to.route.path });
            if(router.to.route.meta.requiresAuth) {
              if (store.getters.getUserToken) {
                let result = await userService.isTokenValid();
                if (result.data.isValid) {
                  router.resolve();
                  return; 
                } else {
                  console.log("TOKEN IS INVALID: ", store.getters.getUserToken)
                  store.dispatch('resetUserData');
                  f7.view.current.router.navigate('/login');
                }
              } else {
                console.log("TOKEN NOT FOUND!")
                store.dispatch('resetUserData');
                f7.view.current.router.navigate('/login');
                return;
              }
            } else {
              router.resolve();
              return;
            }
          }
        },
      };
      return {
        f7params,
        store
      }
    },
    computed: {
      appModeConverted() {
        return store.getters.getAppModeConverted;
      },
      getStoreDestinations() {
        return store.getters.getStoreDestinations;
      }
    },
    beforeCreate() {
      // Assign default settings if we have none yet
      if (store.getters.getApiHost === null || 
          store.getters.getApiUrl === null
      ) {
        store.dispatch('resetAppSettings');
      }
      if (store.getters.getIclNews === null) {
        store.dispatch('resetAppData');
      }
      if (store.getters.getTotalRides === null) {
        store.dispatch('resetWalletData');
      }
    },
    created() {
      // Set event listeners to fetch changes thruout the app 
      this.emitter.on('refresh-ui-elements', () => {
        console.log("refresh-ui-elements called!");
        f7.params.dialog.buttonOk = this.$t('app.dialog.ok');
        f7.params.dialog.buttonCancel = this.$t('app.dialog.cancel');
      });
      // Set event listener to trigger confetti fx
      this.emitter.on('show-confetti', (options) => {
        if (!options.emojis) {
          this.triggerConfetti();
        } else {
          this.triggerEmojiConfetti(options.poop);
        }
      });
    },
    mounted() {
      f7ready(async () => {
        await store.dispatch('setAppSettings');
        this.clearOldDestinations();

        if (getDevice().cordova) {
          cordovaApp.init(f7, store, this.emitter);
        }
        store.dispatch('setNetworkStatus', { networkStatus: navigator.onLine });

        // Add event listener to handle changes in network connection
        window.addEventListener('online', this.updateStatus);
        window.addEventListener('offline', this.updateStatus);

        // Initialize dialog button language
        f7.params.dialog.buttonOk = this.$t('app.dialog.ok');
        f7.params.dialog.buttonCancel = this.$t('app.dialog.cancel');

        // Initilize theme mode
        f7.setDarkMode(this.appModeConverted);

        // Initialize confetti fx container
        if (this.$refs.confettiContainer) {
          this.jsConfetti = new JSConfetti({
            canvas: this.$refs.confettiContainer,
            zIndex: 999999,
          });
        }
      });
    },
    methods: {
      updateStatus() {
        store.dispatch('setNetworkStatus', { networkStatus: navigator.onLine });
      },
      clearOldDestinations() {
        store.dispatch('clearOldDestinations', { days: this.getStoreDestinations });
      },
      isCypressRunning() {
        return typeof window.Cypress !== 'undefined' && window.Cypress;
      },
      triggerConfetti() {
          if (this.jsConfetti) {
              this.jsConfetti.addConfetti({
                confettiNumber: 250,
                confettiColors: [
                    '#FFD700',
                    '#FF69B4',
                    '#1E90FF',
                    '#32CD32',
                    '#8A2BE2',
                ],
              });
          }
          },
      triggerEmojiConfetti(poop) {
          if (this.jsConfetti) {
            let emojis = poop ? ['💩'] : ['🎉', '✨', '🌟', '🥳', '🚀', '💖'];
            this.jsConfetti.addConfetti({
              emojis: emojis,
              confettiNumber: 100,
            });
          }
      },
    },
    beforeUnmount() {
        window.removeEventListener('online', this.updateStatus);
        window.removeEventListener('offline', this.updateStatus);

        this.emitter.off('refresh-ui-elements');
    },
  }
</script>