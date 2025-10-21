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
      
      <NavBar ref="navBar" :title="title" :large="true" :showSearch="false" :showIcons="true" :navBack="true"/>

        <f7-page :page-content="true">
            <f7-block-title medium>{{ this.$t('account.page.favorites.header') }}</f7-block-title>

            <f7-list dividers-ios strong inset>
                <f7-list-item v-for="favorite in filteredFavorites" :key="favorite.id" swipeout :title="favorite.address" :footer="favorite.type">
                    <template #media>
                        <f7-icon :ios="favorite.icon" :md="favorite.icon"></f7-icon>
                    </template>
                    <f7-swipeout-actions right>
                        <f7-swipeout-button @click="openActionsPopover(favorite)">
                            <f7-icon ios="f7:ellipsis" md="material:more_horiz"></f7-icon>
                        </f7-swipeout-button>
                        <f7-swipeout-button delete @click="deleteFavorite(favorite)">
                            <f7-icon ios="f7:trash" md="material:delete"></f7-icon>
                        </f7-swipeout-button>
                    </f7-swipeout-actions>
                </f7-list-item>
            </f7-list>
            <div class="tip-block-container">
                    <div class="tip-icon-wrapper">
                        <i class="f7-icons" style="font-size: 25px !important">checkmark_seal_fill</i>
                    </div>
                    <div class="tip-text-wrapper">
                        <b>{{ this.$t('account.page.favorites.hint.title') }}</b><br />
                        {{ this.$t('account.page.favorites.hint.edit-favorite') }}
                    </div>
                </div>
            <f7-block>
                <f7-button href="#" @click="openNewFavoriteSheet" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:plus_app_fill" md="material:add_box"></f7-icon>&nbsp;{{ this.$t('account.page.favorites.button.addfavorite') }}</f7-button>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" :tabActive="tabActive"/>

        <AddNewFavorite/>
        <EditFavorite/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';
  import $ from "dom7";

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';
  import AddNewFavorite from '../components/newFavorite.vue';
  import EditFavorite from '../components/editFavorite.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Link,
        NavBar,
        ToolBar,
        AddNewFavorite,
        EditFavorite
    },
    data() {
        return {
            title: this.$t('account.page.favorites.title'),
            tabActive: 4,
            actionsToPopover: null,
            editIsDisabled: false
        };
    },
    computed: {
        favorites: {
            get() {
                return this.$store.getters.getFavorites;
            }
        },
        filteredFavorites() {
            return this.favorites.filter(favorite => favorite.type !== 'Home' && favorite.type !== 'Work');
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
        openEditFavoriteSheet(favorite) {
            this.emitter.emit('open-edit-sheet', favorite);
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactMedium");
            f7.sheet.open('.editFavorite');
        },
        openNewFavoriteSheet() {
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactMedium");
            f7.sheet.open('.newFavorite');
        },
        openActionsPopover(favorite) {
            if (favorite.type === 'Home' || 
                favorite.type === 'Work') {
                    this.editIsDisabled = true;
            } else {
                this.editIsDisabled = false;
            }
            this.actionsToPopover = f7.actions.create({
                buttons: [
                    [
                        { 
                            text: this.$t('account.page.favorites.actions.title'), 
                            label: true 
                        },
                        {
                            text: this.$t('account.page.favorites.actions.edit'),
                            disabled: this.editIsDisabled,
                            onClick: () => {
                                this.openEditFavoriteSheet(favorite);
                            },
                        },
                        { 
                            text: this.$t('account.page.favorites.actions.delete'),
                            onClick: (actions, e) => {
                                this.deleteFavorite(favorite);
                            }
                         },
                    ],
                    [{ 
                        text: this.$t('account.page.favorites.actions.cancel'), 
                        color: 'red' 
                    }],
                ],
                convertToPopover: false
            });
            this.actionsToPopover.open();
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
        },
        deleteFavorite(favorite) {
            const index = this.favorites.indexOf(favorite);
            
            if (index !== -1) {
                this.favorites.splice(index, 1);

                this.sendHapticFeedback("CONFIRM", "Success");
                this.$store.dispatch('setFavorites', { favorites: this.favorites });
                
                f7.toast.show({
                    text: this.$t('account.page.favorites.toast.title'),
                    icon: theme.ios
                        ? '<i class="f7-icons">checkmark_alt_circle</i>'
                        : '<i class="material-icons">check_circle</i>',
                    position: 'center',
                    closeTimeout: 2000,
                    destroyOnClose: true
                });
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
.tip-block-container {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px 15px 15px 15px;
    background-color: var(--f7-card-bg-color);
    border-radius: 12px;
    margin: 0px 15px 0px 15px;
}

.tip-icon-wrapper {
    flex-shrink: 0;
}

.tip-text-wrapper {
    flex-grow: 1;
    color: var(--f7-text-color);
}
</style>