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
    <f7-toolbar id="mainToolbar" bottom icons>
        <f7-link
            id="tab1"
            href="javascript:void(0)"
            @click="navigateToPage('/', 'f7-fade')"
            tab-link
        >
            <f7-icon ios="f7:house_alt_fill" md="material:home">
                <f7-badge v-if="homeBadgeCount > 0" color="red">{{ homeBadgeCount }}</f7-badge>
            </f7-icon>
            <span class="tabbar-label">{{ this.$t('toolbar.home') }}</span>
        </f7-link>

        <f7-link
            id="tab2"
            href="javascript:void(0)"
            @click="navigateToPage('/planning', 'f7-fade')"
            tab-link
        >
            <f7-icon ios="f7:map_fill" md="material:map">
                <f7-badge v-if="planningBadgeCount > 0" color="red">{{ planningBadgeCount }}</f7-badge>
            </f7-icon>
            <span class="tabbar-label">{{ this.$t('toolbar.planning') }}</span>
        </f7-link>

        <f7-link
            id="tab3"
            href="javascript:void(0)"
            @click="navigateToPage('/activity', 'f7-fade')"
            tab-link
        >
            <f7-icon ios="f7:square_list_fill" md="material:list_alt">
                <f7-badge v-if="activityBadgeCount > 0" color="red">{{ activityBadgeCount }}</f7-badge>
            </f7-icon>
            <span class="tabbar-label">{{ this.$t('toolbar.activity') }}</span>
        </f7-link>

        <f7-link
            id="tab4"
            href="javascript:void(0)"
            @click="navigateToPage('/account', 'f7-fade')"
            tab-link
        >
            <f7-icon v-if="noUserImage" ios="f7:person_crop_circle" md="material:account_circle">
                <f7-badge v-if="accountBadgeCount > 0" color="red">{{ accountBadgeCount }}</f7-badge>
            </f7-icon>
            <div v-else class="avatar-wrapper">
                <div class="avatar-container">
                    <f7-badge v-if="accountBadgeCount > 0" color="red" class="avatar-badge">{{ accountBadgeCount }}</f7-badge>
                <div 
                    class="avatar-icon" 
                    :style="{ backgroundImage: `url(${userImage})` }"
                ></div>
                </div>
            </div>
            <span class="tabbar-label">{{ this.$t('toolbar.account') }}</span>
        </f7-link>

    </f7-toolbar>
</template>
<script>
    import { f7, f7ready, f7Toolbar } from 'framework7-vue';
    import $ from "dom7";

    import userService from '@/services/userService';

    export default {
        props: {
            tabActive: {
                type: Number,
                default: 1
            },
        },
        components: {
            f7ready,
            f7Toolbar,
        },
        data() {
            return {
                noUserImage: true
            };
        },
        mounted() {
            f7ready(() => {
                this.checkUserImage();
                this.removeActiveTabs();
                this.switchActiveTab(this.tabActive);
            })
        },
        computed: {
            userImage() {
                return this.$store.getters.getUserImage + '?t=' + this.$store.getters.getUserUpdatedImageAt;
            },
            homeBadgeCount: {
                get() {
                    return this.$store.getters.getHomeBadgeCount;
                },
                set(value) {
                    this.$store.dispatch('setHomeBadgeCount', { count: value });
                }
            },
            planningBadgeCount: {
                get() {
                    return this.$store.getters.getPlanningBadgeCount;
                },
                set(value) {
                    this.$store.dispatch('setPlanningBadgeCount', { count: value });
                }
            },
            activityBadgeCount: {
                get() {
                    return this.$store.getters.getActivityBadgeCount;
                },
                set(value) {
                    this.$store.dispatch('setActivityBadgeCount', { count: value });
                }
            },
            accountBadgeCount: {
                get() {
                    return this.$store.getters.getAccountBadgeCount;
                },
                set(value) {
                    this.$store.dispatch('setAccountBadgeCount', { count: value });
                }
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        methods: {
            async checkUserImage() {
                let response = await userService.checkUserImage(this.$store.getters.getUserID);
                if (response.status === 404) {
                    this.noUserImage = true;
                    this.$store.dispatch('setUserImageDefault');
                } else {
                    this.noUserImage = false;
                }
            },
            resetNotifications(data) {
                switch(data) {
                    case '/home':
                    case '/': 
                        this.homeBadgeCount = 0;
                        break;
                    case '/planning': 
                        this.planningBadgeCount = 0;
                        break;
                    case '/activity': 
                        this.activityBadgeCount = 0;
                        break;
                    case '/account': 
                        this.accountBadgeCount = 0;
                        break;
                    default:
                        break;
                }
            },
            removeActiveTabs() {
                $('#tab1').removeClass('tab-link-active');
                $('#tab2').removeClass('tab-link-active');
                $('#tab3').removeClass('tab-link-active');
                $('#tab4').removeClass('tab-link-active');
            },
            switchActiveTab(activeTab) {
                switch (activeTab) {
                    case 1:
                        $('#tab1').addClass('tab-link-active');
                        break;
                    case 2:
                        $('#tab2').addClass('tab-link-active');
                        break;
                    case 3:
                        $('#tab3').addClass('tab-link-active');
                        break;
                    case 4:
                        $('#tab4').addClass('tab-link-active');
                        break;
                    default:
                        break;
                }
            },
            navigateToPage(page, transition) {
                this.resetNotifications(page);
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                f7.view.current.router.navigate(page, { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: transition });
            },
            sendHapticFeedback(androidType, iosType) {
                if (this.hapticFeedback) {
                    this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                        console.error("HAPTIC ERROR: ", error);
                    });
                }
            },
        },
    };
</script>