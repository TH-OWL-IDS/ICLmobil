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
                <div class="grid grid-cols-3 grid-gap">
                    <div>
                        <f7-button href="/help" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" style="height: 80px;" fill>
                            <div class="icon_text_button">
                                <f7-icon color="white" ios="f7:question_circle" md="material:help"></f7-icon>
                                <span style="display: block;">{{ this.$t('account.button.help') }}</span>
                            </div>
                        </f7-button>
                    </div>
                    <div>
                        <f7-button @click="navigateToPage('/wallet', 'f7-fade')" style="height: 80px;" fill>
                            <div class="icon_text_button">
                                <f7-icon color="white" icon="fa-solid fa-leaf" size="28"></f7-icon>
                                <span style="display: block;">{{ this.$t('account.button.wallet') }}</span>
                            </div>
                        </f7-button>
                    </div>
                    <div>
                        <f7-button href="/activity" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" style="height: 80px;" fill>
                            <div class="icon_text_button">
                                <f7-icon color="white" ios="f7:square_favorites_fill" md="material:list_alt"></f7-icon>
                                <span style="display: block;">{{ this.$t('account.button.activity') }}</span>
                            </div>
                        </f7-button>
                    </div>
                </div>
                <div class="grid grid-cols-1">
                    <div>&nbsp;</div>
                </div>
                <div class="grid grid-cols-1">
                    <div>
                        <f7-button @click="navigateToPage('/wallet', 'f7-fade')" large fill style="--f7-button-large-text-transform: none">
                            <div v-html="this.$t('account.button.co2saving')"></div>
                            &nbsp;
                            &nbsp;
                            <f7-icon color="white" icon="fa-solid fa-leaf" size="28"></f7-icon>
                            &nbsp;
                            ~ {{ totalEmmisions }} kg
                        </f7-button>
                    </div>
                </div>
            </f7-block>

            <hr style="width: 90vw; color: #96D35F;"/>

            <f7-block>
                <f7-list strong-ios>
                    <f7-list-item link="#" @click="openSheet('.userData')" chevron-center :title="name" :footer="phone">
                        <template #media>
                            <div 
                                class="avatar-small" 
                                :style="{ backgroundImage: `url(${image})` }"
                            ></div>
                        </template>
                    </f7-list-item>
                </f7-list>
            </f7-block>

            <f7-block>
                <f7-list dividers-ios strong-ios>
                    <f7-list-item link="#" @click="openSheet('.personalAddress')" chevron-center :title="this.$t('account.home-title')" :footer="this.$t('account.home-footer')">
                        <template #media>
                            <f7-icon ios="f7:house" md="material:home"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item link="#" @click="openSheet('.workAddress')" chevron-center :title="this.$t('account.work-title')" :footer="this.$t('account.work-footer')">
                        <template #media>
                            <f7-icon ios="f7:bag" md="material:work"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item link="/favorites" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('account.favorites-title')" :footer="this.$t('account.favorites-footer')">
                        <template #media>
                            <f7-icon ios="f7:map_pin_ellipse" md="material:pin_drop"></f7-icon>
                        </template>
                    </f7-list-item>
                    <f7-list-item link="/messages" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" chevron-center :title="this.$t('account.messages-title')" :footer="this.$t('account.messages-footer')">
                        <template #media>
                            <f7-icon ios="f7:envelope" md="material:mail"></f7-icon>
                        </template>
                    </f7-list-item>
                </f7-list>
            </f7-block>

            <f7-block>
                <f7-button large fill @click="logout"><f7-icon ios="f7:person_crop_circle_badge_checkmark" md="material:account_circle"></f7-icon>&nbsp; {{ this.$t('account.button.logout') }}</f7-button>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page>

        <PersonalData/>
        <PersonalAddressMap/>
        <WorkAddressMap/>

        <ToolBar ref="toolBar" :tabActive="tabActive"/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';
  import PersonalData from '../components/personalData.vue';
  import PersonalAddressMap from '../components/personalAddressMap.vue';
  import WorkAddressMap  from '../components/workAddressMap.vue';

  import userService from '@/services/userService';
  
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
        PersonalData,
        PersonalAddressMap,
        WorkAddressMap
    },
    data() {
        return {
            title: this.$t('account.title'),
            tabActive: 4
        };
    },
    computed: {
        image() {
            this.checkUserImage();
            return this.$store.getters.getUserImage + '?t=' + this.$store.getters.getUserUpdatedImageAt;
        },
        name() {
            return this.$store.getters.getUserName;
        },
        phone() {
            return this.$store.getters.getUserPhone;
        },
        totalEmmisions() {
            return this.$store.getters.getTotalEmmisions;
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
        async checkUserImage() {
            let response = await userService.checkUserImage(this.$store.getters.getUserID);
            if (response.status === 404) {
                this.$store.dispatch('setUserImageDefault');
            }
        },
        openSheet(sheet) {
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            f7.sheet.open(sheet);
        },
        navigateToPage(page, transition) {
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            f7.view.current.router.navigate(page, { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: transition });
        },
        async logout() {
            let response = await userService.logout();
            if (response.status === 200) {
                this.sendHapticFeedback("CONFIRM", "Success");
                this.$store.dispatch('resetUserData');
                f7.view.current.router.navigate('/login', { history: false, clearPreviousHistory: true, ignoreCache: true });
                this.emitter.emit('close-verify-toast');
            } else {
                this.sendHapticFeedback("REJECT", "Error");
                f7.dialog.alert(this.$t('app.dialog.error.servertext'), this.$t('app.dialog.error.title'));
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