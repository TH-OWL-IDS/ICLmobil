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
    <f7-page class="no-swipeback" :page-content="false">
        
        <NavBar ref="navBar" :title="title" :large="true" :showSearch="false" :showIcons="false" :navBack="true"/>

        <f7-page :page-content="true">
            <f7-block>
                <div class="car-pool-setup-header text-align-center block-title block-title-medium">
                    {{ this.$t('preferences.carPoolSetup.header') }}
                </div>
                <img src="../assets/logos/rrive_fill_gray.svg" class="car-pool-setup-image">
                <div class="car-pool-setup-text text-align-center" 
                     v-html="this.$t('preferences.carPoolSetup.text')"
                >
                </div>
                <div class="car-pool-download-button text-align-center">
                    <f7-button href="#" @click="downloadApp" fill large style="--f7-button-large-text-transform: none">
                        {{ this.$t('preferences.carPoolSetup.button.download-app') }}
                    </f7-button>
                </div>
                <div class="car-pool-link-button text-align-center">
                    <div v-if="poolingIsLinked">
                        <i class="f7-icons" style="font-size: 34px;">checkmark_alt_circle</i><br />
                        {{ this.$t('preferences.carPoolSetup.linking-success') }}
                        <div class="linking-hint-small">
                            {{ this.$t('preferences.carPoolSetup.linking-hint') }}
                        </div>
                        <f7-button href="#" @click="openEmail" small style="--f7-button-large-text-transform: none">
                            <f7-icon ios="f7:envelope" md="material:mail" style="font-size: 20px;"></f7-icon>&nbsp;&nbsp;info@rrive.com
                        </f7-button>
                    </div>
                    <f7-button v-else href="#" @click="linkCarPoolApp" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none">
                        <f7-icon ios="f7:link" md="material:link"></f7-icon>&nbsp;{{ this.$t('preferences.carPoolSetup.button.link-app') }}
                    </f7-button>
                </div>
            </f7-block>
            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Link,
        NavBar,
        ToolBar
    },
    data() {
        return {
            title: this.$t('preferences.carPoolSetup.title'),
            appDownloadURL: this.$store.getters.getPoolingDownloadURL,
            poolingRegisterURL: this.$store.getters.getPoolingRegister,
     };
    },
    computed: {
        inAppBrowser() {
            return this.$store.getters.getPluginInAppBrowser;
        },
        userID() {
            return this.$store.getters.getUserID;
        },
        firstname() {
            const name = this.$store.getters.getUserName.split(' ');
            return name[0];
        },
        lastname() {
            const name = this.$store.getters.getUserName.split(' ');
            return name[1];
        },
        email() {
            return this.$store.getters.getUserEmail;
        },
        userToken() {
            return this.$store.getters.getUserToken;
        },
        poolingIsLinked() {
            return this.$store.getters.getPoolingIsLinked;
        },
        poolingAuthKey() {
            return this.$store.getters.getPoolingAuthKey;
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    mounted() {
        f7ready(() => {
        })
    },
    methods: {
        downloadApp() {
            try {
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                if (this.inAppBrowser) {
                    if (f7.device.cordova) {
                        this.inAppBrowser.open(this.appDownloadURL, '_system');
                    }
                }
            } catch(err) {
                console.log("ERROR: ", err)
            }
        },
        linkCarPoolApp() {
            try {
                if (!this.userToken) {
                    f7.dialog.alert(this.$t('app.dialog.error.app-linking-error'), this.$t('app.dialog.error.title'));
                    return;
                }
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                const url = this.poolingRegisterURL + this.userID + '/?firstname=' + this.firstname + '&lastname=' + this.lastname + '&email=' + this.email + '&key=' + this.poolingAuthKey + '/';
                if (this.inAppBrowser) {
                    if (f7.device.cordova) {
                        this.inAppBrowser.open(url, '_system');
                    }
                }
            } catch(err) {
                console.log("ERROR: ", err)
            }
        },
        openEmail() {
            try {
                this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                if (this.inAppBrowser) {
                    if (f7.device.cordova) {
                        this.inAppBrowser.open('mailto:info@rrive.com', '_system');
                    }
                }
            } catch(err) {
                console.log("ERROR: ", err)
            }
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
    .car-pool-setup-header {
        color: rgba(100, 150, 150, 1);
    }
    .car-pool-setup-text {
        color: rgba(100, 150, 150, 1);
    }
    .car-pool-download-button {
        padding-top: 20px;
    }
    .car-pool-link-button {
        padding-top: 20px;
        padding-bottom: calc(var(--f7-toolbar-height) + var(--f7-safe-area-bottom));
    }
    .car-pool-setup-image {
        height: 10vh;
        width: 80vw;
        padding: 20px;
    }
    .linking-hint-small {
        display: block;
        text-align: center;
        color: var(--f7-block-header-text-color);
        font-size: 11px;
        margin: 20px 20px 10px 10px;
    }
</style>