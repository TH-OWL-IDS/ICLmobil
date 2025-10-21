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
    <div v-if="isDevMode" class="dev-mode-badge">
        <i class="icon f7-icons">hammer_fill</i>
        <span>DEV</span>
    </div>
</template>
<script>
    import { f7, f7ready } from 'framework7-vue';

    export default {
        data() {
            return {
                notification: null,
                isVisible: false,
                closeTimeout: 3000
            };
        },
        mounted() {
            f7ready(async () => {
                this.emitter.on('dispatch-push-data', (pushData) => {
                    // This is used if the App is running in foreground
                    this.dispatchPushData(pushData);
                    navigator.vibrate(1000);
                });
                this.emitter.on('navigate-after-push', (pushData) => {
                    // This works only IF the App is running but in background
                    this.navigateToPage(pushData);
                });
                this.emitter.on('show-push-notification', () => {
                    // OBSOLETE: Might not be useful to show inside app
                    this.showNotification('blah', 'blub', 'FOO');
                    navigator.vibrate(1000);
                });
            })
        },
        computed: {
            isDevMode() {
                return this.$store.getters.getDevMode;
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
            walletBadgeCount: {
                get() {
                    return this.$store.getters.getWalletBadgeCount;
                },
                set(value) {
                    this.$store.dispatch('setWalletBadgeCount', { count: value });
                }
            },
            prefsBadgeCount: {
                get() {
                    return this.$store.getters.getPrefsBadgeCount;
                },
                set(value) {
                    this.$store.dispatch('setPrefsBadgeCount', { count: value });
                }
            }
        },
        methods: {
            dispatchPushData(data) {
                switch(data) {
                    case '/home':
                    case '/': 
                        this.homeBadgeCount += 1;
                        break;
                    case '/planning': 
                        this.planningBadgeCount += 1;
                        break;
                    case '/activity': 
                        this.activityBadgeCount += 1;
                        break;
                    case '/account': 
                        this.accountBadgeCount += 1;
                        break;
                    case '/wallet': 
                        this.walletBadgeCount += 1;
                        break;
                    case '/preferences': 
                        this.prefsBadgeCount += 1;
                        break;
                    default:
                        break;
                }
            },
            showNotification(title, subtitle, text) {
                this.isVisible = true;
                this.notification = f7.notification.create({
                    icon: '<i class="icon icon-f7"></i>',
                    title: title,
                    titleRightText: 'now',
                    subtitle: subtitle,
                    text: text,
                    closeTimeout: this.closeTimeout,
                    closeOnClick: true,
                    on: {
                        close() {
                            this.isVisible = false;
                        },
                    },
                });
            },
            navigateToPage(page) {
                f7.view.current.router.navigate(page);
            }
        }
    };
</script>
<style scoped>
.dev-mode-badge {
    position: fixed;
    bottom: calc(var(--f7-toolbar-height) + env(safe-area-inset-bottom) + 10px);
    right: 10px;
    background-color: #ff3b30;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 4px;
    z-index: 99;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.dev-mode-badge i {
    font-size: 14px;
}
</style>