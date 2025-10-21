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
    <f7-navbar sliding :large="large">
        <f7-nav-left v-if="navBack">
            <f7-link @click="navigateBack" icon-ios="f7:chevron_left" icon-md="material:arrow_back">&nbsp;{{ this.$t('navbar.link.back') }}</f7-link>
        </f7-nav-left>
        <f7-nav-title>
            <div v-html="title"></div>
        </f7-nav-title>
        <f7-nav-title-large v-if="large">
            <div v-html="title"></div>
        </f7-nav-title-large>
        <f7-subnavbar v-if="showSearch" :inner="false">
            <f7-searchbar 
                :placeholder="this.$t('navbar.search.placeholder')" 
                :disable-button-text="this.$t('navbar.search.cancel')" 
                @input="onInput"
                @focus="onFocus">
            </f7-searchbar>
        </f7-subnavbar>
        <f7-nav-right>
            <f7-link icon-only v-if="showEdit" href="#" @click="editFavorites">
                <f7-icon v-if="isEditFavoritesMode" f7="pencil" size="28" style="color: #555;"></f7-icon>
                <f7-icon v-else f7="pencil" size="28" style="color: #96D35F;"></f7-icon>
            </f7-link>
            <f7-link icon-only v-if="showIcons" href="#" @click="navigateToPage('/wallet', 'f7-fade')">
                <f7-icon style="color: #96D35F;" icon="fa-solid fa-leaf" size="28">
                    <f7-badge v-if="walletBadgeCount > 0" color="red">{{ walletBadgeCount }}</f7-badge>
                </f7-icon>
            </f7-link>
            <f7-link v-if="showIcons" href="#" @click="navigateToPage('/preferences', 'f7-fade')">
                <f7-icon style="color: #96D35F;" size="28" icon="fa-solid fa-gear">
                    <f7-badge v-if="prefsBadgeCount > 0" color="red">{{ prefsBadgeCount }}</f7-badge>
                </f7-icon>
            </f7-link>
        </f7-nav-right>
    </f7-navbar>
</template>
<script>
    import {
        f7,
        f7Navbar,
        f7Subnavbar,
        f7Searchbar,
        f7NavRight
    } from 'framework7-vue';

    export default {
        props: {
            title: {
                type: String,
                default: 'Default Title'
            },
            large: {
                type: Boolean,
                default: false
            },
            showSearch: {
                type: Boolean,
                default: false
            },
            showIcons: {
                type: Boolean,
                default: true
            },
            navBack: {
                type: Boolean,
                default: false
            },
            showEdit: {
                type: Boolean,
                default: false
            }
        },
        components: {
            f7,
            f7Navbar,
            f7Subnavbar,
            f7Searchbar,
            f7NavRight
        },
        data() {
            return {
                isEditFavoritesMode: false,
                searchQuery: '',
                debounceTimer: null,
                debounceTimeout: 500,
            };
        },
        computed: {
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
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        methods: {
            onInput(event) {
                this.searchQuery = event.target.value;
                this.searchQuery.trim();
                
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.$emit('search', this.searchQuery);
                }, this.debounceTimeout);
            },
            onFocus() {
                this.sendHapticFeedback("SEGMENT_TICK", "SelectionChanged");
            },
            resetNotifications(data) {
                switch(data) {
                    case '/wallet': 
                        this.walletBadgeCount = 0;
                        break;
                    case '/preferences': 
                        this.prefsBadgeCount = 0;
                        break;
                    default:
                        break;
                }
            },
            editFavorites() {
                this.sendHapticFeedback('SEGMENT_TICK', 'SelectionChanged');
                this.emitter.emit('enable-edit-favorites', '');
                this.isEditFavoritesMode = !this.isEditFavoritesMode;
                if (this.isEditFavoritesMode) {
                    this.emitter.emit('close-last-destinations', '');
                } else {
                    this.emitter.emit('open-last-destinations', '');
                }
            },
            navigateToPage(page, transition) {
                this.resetNotifications(page);
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                this.emitter.emit('close-last-destinations', '');
                f7.view.current.router.navigate(page, { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: transition });
            },
            navigateBack() {
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
                f7.view.current.router.back({ history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: 'f7-push' });
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