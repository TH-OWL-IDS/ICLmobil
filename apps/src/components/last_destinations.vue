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
    <f7-sheet @sheet:opened="init"
              @sheet:closed="onClose"
              swipe-to-close
              swipe-to-step
              :style="{ height: sheetHeight }"
              :close-by-outside-click="true"
              :backdrop="false"
              @sheet:stepopen="maximizeSheet"
              @sheet:stepclose="minimizeSheet"
              class="last-destinations-sheet">
        <template #fixed>
            <div class="swipe-handler" ></div>
        </template>

        <f7-toolbar class="sheet-toolbar-top">
            <div class="left sheet-title">
                {{ title }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-toolbar class="sheet-toolbar">
            <div class="searchbar searchbar-inner sheet-searchbar">
                <div class="searchbar-input-wrap">
                    <input type="search" 
                        :placeholder="this.$t('planning.sheet.yourdestination.search.placeholder')" 
                        @input="onInput" 
                        @focus="onFocus" 
                        @blur="onBlur"
                        @keyup.enter="onEnter" 
                        v-model="searchQuery" />
                    <i class="searchbar-icon"></i>
                    <span class="input-clear-button" @click="clearSearch"></span>
                </div>
            </div>
        </f7-toolbar>
        <div class="sheet-modal-swipe-step"></div>

        <f7-page-content>
            <f7-block v-if="searchResults.length">
                <f7-block-title medium>{{ this.$t('planning.sheet.yourdestination.resultstitle') }}</f7-block-title>
                <f7-list>
                    <div v-for="(result, index) in searchResults" :key="index">
                        <f7-list-item link="#" @click="selectResult(result)" :title="`${result.name}`">
                            <template #media>
                                <f7-icon ios="f7:map_pin_ellipse" md="material:pin_drop"></f7-icon>
                            </template>
                        </f7-list-item>
                    </div>
                </f7-list>
            </f7-block>

            <f7-block v-if="showFavorites">
                <f7-block-title medium>{{ this.$t('planning.sheet.yourdestination.favoritestitle') }}</f7-block-title>
                <f7-list dividers-ios strong>
                    <f7-list-item 
                        v-for="favorite in favorites" 
                        :key="favorite.id" 
                        :title="favorite.address" 
                        :footer="favorite.type"
                        @click="selectFavorite(favorite)">
                        <template #media>
                            <f7-icon :ios="favorite.icon" :md="favorite.icon"></f7-icon>
                        </template>
                    </f7-list-item>
                </f7-list>
                
            </f7-block>

            <f7-block v-if="showLastDestinations">
                <f7-block-title v-if="lastDestinations.length > 0" medium>{{ this.$t('planning.sheet.yourdestination.lastdestinationstitle') }}</f7-block-title>
                <f7-list dividers-ios strong>
                    <f7-list-item 
                        v-for="lastDestination in lastDestinations" 
                        :key="lastDestination.id" 
                        :title="lastDestination.address"
                        @click="selectLastDestination(lastDestination)">
                        <template #media>
                            <f7-icon ios="f7:clock" md="material:schedule"></f7-icon>
                        </template>
                        <template #after>
                            <f7-icon 
                                ios="f7:star" 
                                md="material:star_outline"
                                @click="makeFavorite(lastDestination)"></f7-icon>
                        </template>
                    </f7-list-item>
                </f7-list>
            </f7-block>
            <f7-block>
                <f7-block-title large>&nbsp;</f7-block-title>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page-content>
    </f7-sheet>
</template>
<script>
    import {
        f7,
        f7Sheet,
        f7ready
    } from 'framework7-vue';

    export default {
        props: {
            title: String,
            searchResults: {
                type: Array,
                default: () => [],
            },
        },
        components: {
            f7Sheet
        },
        data() {
            return {
                searchQuery: '',
                debounceTimer: null,
                debounceTimeout: 500,
                sheetHeight: '45vh',
                showFavorites: true,
                showLastDestinations: true,
                sheetMinimized: true
            };
        },
        created() {
            this.emitter.on('close-last-destinations', () => {
                this.closeSheet();
            });
            this.emitter.on('open-last-destinations', () => {
                this.openSheet();
            });
        },
        computed: {
            favorites: {
                get() {
                    return this.$store.getters.getFavorites;
                }
            },
            lastDestinations: {
                get() {
                    return this.$store.getters.getLastDestinations;
                }
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        methods: {
            init() {
                console.log("SHEET LAST DESTINATONS OPENED!")
                this.emitter.emit('refresh-map-planning', '');
            },
            onClose() {
                console.log("SHEET CLOSING")
                this.sheetHeight = '45vh';
                this.sheetMinimized = true;
                this.emitter.emit('refresh-map-planning', '');
            },
            makeFavorite(lastDestination) {
                const index = this.lastDestinations.indexOf(lastDestination);
                if (index !== -1) {
                    this.lastDestinations.splice(index, 1);
                }
                const maxId = this.favorites.reduce((max, entry) => Math.max(max, entry.id), 0);
                var newEntryID = maxId + 1;
                var newEntry = {
                    id: newEntryID, address: lastDestination.address, type: "Adresse", lat: lastDestination.lat, long: lastDestination.long, icon: "f7:map_pin_ellipse"
                }
                this.favorites.push(newEntry);

                this.$store.dispatch('setLastDestinations', { lastDestinations: this.lastDestinations });
                this.$store.dispatch('setFavorites', { favorites: this.favorites });
                this.sendHapticFeedback('CONFIRM', 'ImpactLight');
            },
            addLastDestination(address, latitude, longitude) {
                const maxId = this.lastDestinations.reduce((max, entry) => Math.max(max, entry.id), 0);
                var newEntryID = maxId + 1;
                let now = new Date().toISOString();
                var newEntry = {
                    id: newEntryID, address: address, type: "Adresse", lat: latitude, long: longitude, icon: "f7:map_pin_ellipse", added: now
                }                
                this.lastDestinations.unshift(newEntry);
                if (this.lastDestinations.length > 5) {
                    this.lastDestinations.pop();
                }
                this.$store.dispatch('setLastDestinations', { lastDestinations: this.lastDestinations });
            },
            searchForAddress(address) {
                this.searchQuery = address;
                this.$emit('search', this.searchQuery);
                this.$emit('update-search-query', this.searchQuery);
                this.toggleSwipeStep();
            },
            maximizeSheet() {
                this.sheetMinimized = false;
            },
            minimizeSheet() {
                this.sheetMinimized = true;
            },
            onFocus(event) {
                event.preventDefault();
                event.stopPropagation();
                this.stepSwitchSheet(true);
            },
            onBlur(event) {
                event.preventDefault();
                event.stopPropagation();
                this.stepSwitchSheet(false);
            },
            onInput(event) {
                this.hideFavorites = true;
                this.searchQuery = event.target.value;

                if (this.searchQuery.trim() === '') {
                    this.clearSearch();
                }

                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.$emit('search', this.searchQuery);
                    this.$emit('update-search-query', this.searchQuery);
                }, this.debounceTimeout);
            },
            onEnter(event) {
                event.preventDefault();
                event.stopPropagation();
                this.$emit('search', this.searchQuery);
            },
            onEnter(event) {
                event.preventDefault();
                event.stopPropagation();
                this.$emit('search', this.searchQuery);
            },
            selectResult(result) {
                this.sheetHeight = '45vh';
                this.searchQuery = result.name;
                this.$emit('pickResult', result);
                this.addLastDestination(this.searchQuery, result.lat, result.long);
                this.stepSwitchSheet(false);
            },
            selectFavorite(favorite) {
                this.sheetHeight = '45vh';
                this.$emit('pickFavorite', favorite);
                this.stepSwitchSheet(false);
            },
            selectLastDestination(lastDestination) {
                this.sheetHeight = '45vh';
                this.$emit('pickLastDestination', lastDestination);
                this.stepSwitchSheet(false);
            },
            clearSearch() {
                this.searchQuery = '';
                this.$emit('update-search-query', '');
            },
            toggleSwipeStep() {
                if (this.sheetMinimized)
                    this.sheetMinimized = false;
                else
                    this.sheetMinimized = true;
                
                f7.sheet.stepToggle('.last-destinations-sheet');
                this.emitter.emit('refresh-map-planning', '');
            },
            stepSwitchSheet(stepOpen) {
                if (stepOpen) { 
                    f7.sheet.stepOpen('.last-destinations-sheet');
                } else {
                    f7.sheet.stepClose('.last-destinations-sheet');
                }
                this.emitter.emit('refresh-map-planning', '');
            },
            openSheet() {
                f7.sheet.open('.last-destinations-sheet');
            },
            closeSheet() {
                this.sheetMinimized = false;
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close('.last-destinations-sheet');
            },
            sendHapticFeedback(androidType, iosType) {
                if (this.hapticFeedback) {
                    this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                        console.error("HAPTIC ERROR: ", error);
                    });
                }
            }
        },
        beforeUnmount() {
            this.emitter.off('close-last-destinations');
            this.emitter.off('open-last-destinations');
        }
    };
</script>