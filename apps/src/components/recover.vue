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
              swipe-handler=".swipe-handler" 
              style="min-height: 80vh" 
              swipe-to-close
              push
              backdrop
              :close-by-backdrop-click="true" 
              :close-by-outside-click="true" 
              class="recover">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar">
            <div class="left sheet-title">
                {{ title }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-page-content>
            <f7-block class="no-padding-top no-margin-top">
                <div class="recover-text text-align-center" 
                     v-html="this.$t('login.sheet.recover-text')">
                </div>
                <form @submit.prevent @reset.prevent>
                    <f7-list strong-ios dividers-ios inset>
                        <f7-list-input 
                            :label="this.$t('login.sheet.email-label')" 
                            :value="recoverEmail"
                            v-model:value="recoverEmail" 
                            :disabled="true"
                        ></f7-list-input>
                        <f7-list-input 
                            :label="this.$t('login.sheet.code-label')" 
                            :placeholder="this.$t('login.sheet.code-placeholder')"
                            :error-message="this.$t('login.sheet.code-error')"
                            :error-message-force="v$.code.$error"
                            :value="code"
                            @input="code = $event.target.value"
                            @blur="v$.code.$touch"
                            v-model:value="code" 
                        ></f7-list-input>
                        <f7-list-input 
                            :label="this.$t('login.sheet.password-label')" 
                            type="password"
                            :placeholder="this.$t('login.sheet.password-placeholder')"
                            :error-message="this.$t('login.sheet.password-error')"
                            :error-message-force="v$.newPassword.$error"
                            :value="newPassword"
                            @input="newPassword = $event.target.value"
                            @blur="v$.newPassword.$touch"
                            v-model:value="newPassword" 
                        ></f7-list-input>
                    </f7-list>

                    <div class="recover-hint text-align-center">
                        <f7-icon ios="f7:exclamationmark_triangle" md="material:warning"></f7-icon>
                        {{ this.$t('login.sheet.recover-hint') }}
                    </div>

                    <div class="button-wrapper">
                        <f7-button large fill @click="recover">
                            {{ this.$t('login.sheet.button.set-new-password') }}
                        </f7-button>
                    </div>
                </form>
            </f7-block>
            <f7-block>
                <f7-block-title medium></f7-block-title>
            </f7-block>
        </f7-page-content>
    </f7-sheet>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';

    import useVuelidate from '@vuelidate/core'
    import { required } from '@vuelidate/validators';

    import userService from '../services/userService';
  
    export default {
        components: {
            f7,
            f7ready,
            f7Page,
            f7Block,
            f7Link
        },
        data() {
            return {
                title: this.$t('login.sheet.title'),
                recoverEmail: null,
                code: null,
                newPassword: null
            };
        },
        setup() {
            return { v$: useVuelidate({ $scope: false }) }
        },
        validations() {
            return {
                code: {
                    required
                },
                newPassword: {
                    required
                }
            }
        },
        created() {
            this.emitter.on('set-recover-email', (email) => {
                this.recoverEmail = email.toLowerCase();
            });
        },
        methods: {
            init() {
                console.log("SHEET RECOVER OPENED");
                console.log("EMAIL: ", this.recoverEmail)
            },
            onClose() {
                console.log("SHEET CLOSING")
                this.recoverEmail = null;
                this.code = null;
                this.newPassword = null;
                this.v$.$reset();
            },
            async recover() {
                try {
                    this.v$.$touch();
                    if (this.v$.$invalid)
                        return;

                    const data = {
                        email: this.recoverEmail.toLowerCase(),
                        code: this.code,
                        newPassword: this.newPassword
                    }

                    const response = await userService.reset(data);
                    if (response.status === 200) {
                        f7.toast.show({
                            text: this.$t('login.sheet.toast.success'),
                            icon: theme.ios
                                ? '<i class="f7-icons">checkmark_alt_circle</i>'
                                : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                    } else if (response.status === 409) {
                        f7.dialog.alert(this.$t('app.dialog.error.wrong-code'), this.$t('app.dialog.error.title'));
                    } else {
                        f7.dialog.alert(this.$t('app.dialog.error.text'), this.$t('app.dialog.error.title'));
                    }
                    this.closeSheet();
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            closeSheet() {
                f7.sheet.close('.recover');
            }
        },
        beforeUnmount() {
            this.emitter.off('set-recover-email');
        }
    };
</script>

<style scoped>
    .button-wrapper {
        padding-bottom: 30px;
    }
</style>