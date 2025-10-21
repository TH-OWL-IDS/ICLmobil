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
    <f7-page :page-content="false">
      
        <NavBar ref="navBar" :title="title" :large="true" :showSearch="false" :showIcons="true"/>
        
        <f7-page :page-content="true">
            <f7-block>
                <f7-block-title medium>{{ this.$t('preferences.appsettings.title') }}</f7-block-title>
                <f7-list dividers-ios strong-ios>
                    <f7-list-item data-cy="prefs-faceid-fld" :title="this.$t('preferences.appsettings.faceid')">
                        <template #media>
                            <f7-icon ios="f7:lock_shield" md="material:verified_user"></f7-icon>
                        </template>
                        <template #after>
                            <f7-toggle data-cy="prefs-faceid-tgl" v-model:checked="faceIDLogin" />
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-lang-fld" :title="this.$t('preferences.appsettings.language')">
                        <template #media>
                            <f7-icon ios="f7:globe" md="material:language"></f7-icon>
                        </template>
                        <template #footer>
                            {{ selectedLanguageLabel }}
                        </template>
                        <template #after>
                            <div class="select-wrapper">
                                 <select v-model="selectedLanguage" @change="onLanguageChange" class="select">
                                    <option value="en">{{ this.$t('preferences.languages.english') }}</option>
                                    <option value="de">{{ this.$t('preferences.languages.german') }}</option>
                                </select>
                                <f7-icon ios="f7:chevron_up_chevron_down" md="material:unfold_more" size="20px"></f7-icon>
                            </div>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-store-dest-fld" :title="this.$t('preferences.appsettings.storedestinations')">
                        <template #media>
                            <f7-icon ios="f7:clock" md="material:schedule"></f7-icon>
                        </template>
                        <template #footer>
                            {{ selectedStoreDestinationLabel }}
                        </template>
                        <template #after>
                            <div class="select-wrapper">
                                 <select v-model="selectedStoreDestinations" @change="onStoreDestinationsChange" class="select">
                                    <option value="7">{{ this.$t('preferences.storagetime.7days') }}</option>
                                    <option value="14">{{ this.$t('preferences.storagetime.14days') }}</option>
                                    <option value="30">{{ this.$t('preferences.storagetime.30days') }}</option>
                                </select>
                                <f7-icon ios="f7:chevron_up_chevron_down" md="material:unfold_more" size="20px"></f7-icon>
                            </div>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-mode-fld" :title="this.$t('preferences.appsettings.darkmode')">
                        <template #media>
                            <f7-icon ios="f7:moon_fill" md="material:dark_mode"></f7-icon>
                        </template>
                        <template #footer>
                            {{ selectedAppModeLabel }}
                        </template>
                        <template #after>
                            <div class="select-wrapper">
                                 <select v-model="selectedAppMode" @change="onAppModeChange" class="select">
                                    <option value="light">{{ this.$t('preferences.appmode.light') }}</option>
                                    <option value="dark">{{ this.$t('preferences.appmode.dark') }}</option>
                                    <option value="system">{{ this.$t('preferences.appmode.system') }}</option>
                                </select>
                                <f7-icon ios="f7:chevron_up_chevron_down" md="material:unfold_more" size="20px"></f7-icon>
                            </div>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-reset-tours-fld" :title="this.$t('preferences.appTours.appTours-title')" link="#" @click="resetTours">
                        <template #media>
                            <f7-icon ios="f7:arrow_counterclockwise" md="material:replay"></f7-icon>
                        </template>
                        <template #footer>
                            {{ this.$t('preferences.appTours.appTours-footer') }}
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-pool-setup-fld" :title="this.$t('preferences.carPoolSetup.carPoolSetup-title')" link="/carPoolSetup" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')">
                        <template #media>
                            <f7-icon ios="f7:car_fill" md="material:directions_car"></f7-icon>
                        </template>
                        <template #footer>
                            {{ this.$t('preferences.carPoolSetup.carPoolSetup-footer') }}
                        </template>
                    </f7-list-item>
                </f7-list>
            </f7-block>

            <f7-block v-if="userToken">
                <f7-block-title medium>{{ this.$t('preferences.appsecurity.title') }}</f7-block-title>
                <f7-list dividers-ios strong-ios>
                    <f7-list-item data-cy="prefs-delete-account-lnk" link="/deleteAccount" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('preferences.appsecurity.account-title')" :footer="this.$t('preferences.appsecurity.account-footer')">
                        <template #media>
                            <f7-icon ios="f7:person_crop_circle_fill" md="material:account_circle"></f7-icon>
                        </template>
                    </f7-list-item>
                </f7-list>
            </f7-block>

            <f7-block>
                <f7-block-title medium>{{ this.$t('preferences.appinfo.title') }}</f7-block-title>
                <f7-list dividers-ios strong-ios>
                    <f7-list-item data-cy="prefs-help-lnk" link="/help" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('preferences.appinfo.help')">
                        <template #media>
                            <f7-icon ios="f7:question_circle" md="material:help"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-data-lnk" link="/dataProtection" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('preferences.appsecurity.dataprotection-title')">
                        <template #media>
                            <f7-icon ios="f7:lock_fill" md="material:lock"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-legal-lnk" link="/legal" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('preferences.appinfo.legal')">
                        <template #media>
                            <f7-icon ios="f7:checkmark_seal" md="material:gavel"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-imprint-lnk" link="/imprint" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('preferences.appinfo.imprint')">
                        <template #media>
                            <f7-icon ios="f7:text_quote" md="material:cookie"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item data-cy="prefs-about-lnk" link="/about" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('preferences.appinfo.about')">
                        <template #media>
                            <f7-icon ios="f7:info_circle" md="material:info"></f7-icon>
                        </template>
                    </f7-list-item>
                </f7-list>

                <div v-if="userToken" class="button-wrapper">
                    <f7-button data-cy="prefs-feedback-btn" href="#" @click="leaveFeedback" fill large style="color: #444; background-color: #ccc !important; --f7-button-large-text-transform: none"><i class="icon f7-icons" style="font-size: 22px">hand_thumbsup_fill</i>&nbsp;{{ this.$t('preferences.button.app-feedback') }}</f7-button>
                </div>

                <div v-else class="page-padding"></div>
            </f7-block>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>
        <AppFeedback/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import AppFeedback from '../components/feedback.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Tabs,
        f7Tab,
        f7Link,
        NavBar,
        ToolBar,
        AppFeedback
    },
    data() {
        return {
            selectedLanguage: this.$store.getters.getAppLanguage,
            selectedStoreDestinations: this.$store.getters.getStoreDestinations,
            selectedAppMode: this.$store.getters.getAppMode,
            selectedAppModeLong: this.$t('preferences.appmode.light'),
            languages: {
                en: this.$t('preferences.languages.english'),
                de: this.$t('preferences.languages.german'),
            },
            storageTime: {
                '7': this.$t('preferences.storagetime.7days'),
                '14':  this.$t('preferences.storagetime.14days'),
                '30': this.$t('preferences.storagetime.30days'),
            },
            appMode: {
                'light': this.$t('preferences.appmode.light'),
                'dark': this.$t('preferences.appmode.dark'),
                'system': this.$t('preferences.appmode.system')
            },
     };
    },
    computed: {
        title() {
            return this.$t('preferences.title');
        },
        userToken() {
            return this.$store.getters.getUserToken;
        },
        selectedLanguageLabel() {
            return this.languages[this.selectedLanguage];
        },
        selectedStoreDestinationLabel() {
            return this.storageTime[this.selectedStoreDestinations];
        },
        selectedAppModeLabel() {
            return this.appMode[this.selectedAppMode];
        },
        faceIDLogin: {
            get() {
                return this.$store.getters.getFaceIDLogin;
            },
            set(v) {
                this.sendHapticFeedback("TOGGLE_ON", "SelectionChanged");
                this.$store.dispatch('setFaceIDLogin', { faceid: v });
            }
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    methods: {
        onLanguageChange(event) {
            this.selectedLanguage = event.target.value;
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            this.$store.dispatch('setAppLanguage', { language: this.selectedLanguage });
            this.$i18n.locale = this.selectedLanguage;
            this.emitter.emit('refresh-ui-elements');
        },
        onStoreDestinationsChange(event) {
            switch(event.target.value) {
                case "7":
                    this.selectedStoreDestinationsLong =  this.$t('preferences.storagetime.7days');
                case "14":
                    this.selectedStoreDestinationsLong =  this.$t('preferences.storagetime.14days');
                case "30":
                    this.selectedStoreDestinationsLong =  this.$t('preferences.storagetime.30days');
            }
            this.selectedStoreDestinations = event.target.value;
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            this.$store.dispatch('setStoreDestinations', { days: this.selectedStoreDestinations });
        },
        onAppModeChange(event) {
            switch(event.target.value) {
                case "light":
                    this.selectedAppModeLong = this.$t('preferences.appmode.light');
                    f7.setDarkMode(false);
                    break;
                case "dark":
                    this.selectedAppModeLong = this.$t('preferences.appmode.dark');
                    f7.setDarkMode(true);
                    break;
                case "system":
                    this.selectedAppModeLong = this.$t('preferences.appmode.system');
                    f7.setDarkMode('auto');
                    break;
            }
            this.selectedAppMode = event.target.value;
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            this.$store.dispatch('setAppMode', { mode: this.selectedAppMode });
        },
        resetTours() {
            this.sendHapticFeedback("CONFIRM", "Success");
            f7.dialog.alert(this.$t('preferences.appTours.dialog.text'), this.$t('preferences.appTours.dialog.title'));
            this.$store.dispatch('resetTourData');
        },
        leaveFeedback() {
            this.emitter.emit('open-feedback');
        },
        navigateToPage(page) {
            f7.view.current.router.navigate(page, { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: 'f7-push' });
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
    .button-wrapper {
        padding-bottom: calc(var(--f7-toolbar-height) + var(--f7-safe-area-bottom));
    }
    .select-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .select {
        flex: 1;
        margin-right: 5px;
        padding-right: 5px;
        text-align: right;
    }
    f7-icon {
        flex-shrink: 0;
    }
</style>