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
                <div class="delete-account-header text-align-center block-title block-title-medium">
                    {{ this.$t('preferences.appsecurity.account-header') }}
                </div>
                <div class="delete-account-background"></div>
                <div class="delete-account-text text-align-center" 
                     v-html="this.$t('preferences.appsecurity.account-text')"
                >
                </div>
                <div class="delete-account-button text-align-center">
                    <f7-button href="#" @click="deleteAccount" fill large style="background-color: #FF0000 !important; --f7-button-large-text-transform: none">
                        {{ this.$t('preferences.appsecurity.button.delete-account') }}
                    </f7-button>
                </div>
            </f7-block>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';
  
  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import userService from '@/services/userService';

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
            title: this.$t('preferences.page.account.title'),
     };
    },
    mounted() {
        f7ready(() => {

        })
    },
    methods: {
        deleteAccount() {
            try {
                f7.dialog.confirm(this.$t('preferences.appsecurity.dialog.confirm-delete'), async () => {
                    const response = await userService.deleteUser();
                    if (response.msg) {
                        f7.toast.show({
                            text: this.$t('preferences.appsecurity.toast.success'),
                            icon: theme.ios
                                ? '<i class="f7-icons">checkmark_alt_circle</i>'
                                : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                        this.$store.dispatch('resetUserData');
                        f7.view.current.router.navigate('/login', { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: 'f7-fade' });
                    } else if (response.error) {
                        f7.dialog.alert(this.$t('app.dialog.error.bad-request'), this.$t('app.dialog.error.title'));
                    }
                });
            } catch (err) {
                console.log("ERROR: ", err);
            }
        }
    },
  };
</script>
<style scoped>
    .delete-account-header {
        color: rgba(100, 150, 150, 1);
    }
    .delete-account-text {
        color: rgba(100, 150, 150, 1);
    }
    .delete-account-button {
        padding-top: 20px;
        padding-bottom: calc(var(--f7-toolbar-height) + var(--f7-safe-area-bottom));
    }
</style>