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
</template>
<script>
    import { f7, f7ready } from 'framework7-vue';
    import $ from "dom7";

    import userService from '../services/userService';

    export default {
        data() {
            return {
                toast: null,
                toastVisible: false,
                toastMessage: '',
                toastDismissed: false,
                dismissCount: 0,
                dismissTimer: null,
                dismissDelay: 60000,
                dismissOK: 8000
            };
        },
        mounted() {
            f7ready(async () => {
                f7.on('routeChange', (_route) => {
                    if (this.phone_unverified) {
                        this.showToast(this.$t('app.toast.verify.titlePhone'));
                    } else if (this.email_unverified) {
                        this.showToast(this.$t('app.toast.verify.titleEmail'));
                    }
                    if (this.userID && !this.poolingIsLinked) {
                        this.updatePoolLinkStatus();
                    }
                });
                this.emitter.on('show-verify-toast', () => {
                    if (this.phone_unverified) {
                        this.showToast(this.$t('app.toast.verify.titlePhone'), true);
                    } else if (this.email_unverified) {
                        this.showToast(this.$t('app.toast.verify.titleEmail'), true);
                    }
                });
                this.emitter.on('close-verify-toast', () => {
                    this.closeToast();
                });
            })
        },
        computed: {
            userID() {
                return this.$store.getters.getUserID;
            },
            phone_verified: {
                get() {
                    return this.$store.getters.getUserPhone;
                },
                set(v) {
                    this.$store.dispatch('setUserPhone', { phone: v });
                }
            },
            phone_unverified: {
                get() {
                    return this.$store.getters.getUserPhoneUnverified;
                },
                set(v) {
                    this.$store.dispatch('setUserPhoneUnverified', { phone: v });
                }
            },
            email_verified: {
                get() {
                    return this.$store.getters.getUserEmail;
                },
                set(v) {
                    this.$store.dispatch('setUserEmail', { email: v });
                }
            },
            email_unverified: {
                get() {
                    return this.$store.getters.getUserEmailUnverified;
                },
                set(v) {
                    this.$store.dispatch('setUserEmailUnverified', { email: v });
                }
            },
            poolingIsLinked: {
                get() {
                    return this.$store.getters.getPoolingIsLinked;
                },
                set(v) {
                    this.$store.dispatch('setPoolingIsLinked', { status: v });
                }
            },
            poolingAuthKey: {
                get() {
                    return this.$store.getters.getPoolingAuthKey;
                },
                set(v) {
                    this.$store.dispatch('setPoolingAuthKey', { key: v });
                }
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        methods: {
            async updatePoolLinkStatus() {
                try {
                    const response = await userService.getUserData();
                    if (response.status === 200) {
                        this.poolingIsLinked = response.data.pooling_is_linked;
                        this.poolingAuthKey = response.data.auth_key_external_service;
                    } else {
                        console.log("ERROR getUserData: ", response.status)
                    }
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            showToast(text, force = false) {
                if (!force) {
                    if (this.toastDismissed) return;
                }

                this.sendHapticFeedback('REJECT', 'Error');
                this.toast = f7.toast.create({
                    text: `
                        <table>
                            <tr>
                                <td width="40"><i class="f7-icons">checkmark_seal_fill</i></td>
                                <td>` + text + `<br />
                                    <br />
                                    <button id="validate" class="button button-small button-fill button-round">` + this.$t('app.toast.verify.button') + `</button></td>
                            </tr>
                        </table>`,
                    closeButton: true,
                    closeButtonText: this.$t('app.toast.verify.close'),
                    position: 'top',
                    destroyOnClose: true,
                    on: {
                        close: () => {
                            this.toastDismissed = true;
                            this.startDismissTimer();
                        },
                    },
                });
                this.toast.open();
                this.$nextTick(() => {
                    const button = $('#validate');
                    if (button.length > 0) {
                        button.on('click', this.startValidation);
                    }
                });
            },
            closeToast() {
                if (this.toast) {
                    this.toast.close();
                }
            },
            startDismissTimer() {
                if (this.dismissCount === 1) {
                    this.dismissDelay = 5 * 60 * 1000;  // increase timer to 5 Minutes
                } else if (this.dismissCount === 2) {
                    this.dismissDelay = 10 * 60 * 1000; // increase timer to 10 Minutes
                } else if (this.dismissCount > 2) {
                    this.dismissDelay = 15 * 60 * 1000; // increase timer to 15 Minutes
                    this.dismissCount = 0;
                }
                this.dismissTimer = setTimeout(() => {
                    this.toastDismissed = false;
                    this.dismissCount++;
                }, this.dismissDelay);
            },
            clearDismissTimer() {
                if (this.dismissTimer) {
                    clearTimeout(this.dismissTimer);
                    this.dismissTimer = null;
                }
            },
            startValidation() {
                this.closeToast();
                if (this.phone_unverified) { 
                    this.startPhoneVerification();  
                    return; 
                } else if (this.email_unverified) { 
                    this.startEmailVerification();  
                    return; 
                }
            },
            async startPhoneVerification() {
                console.log("STARTING PHONE VERIFICATION PROCESS ...");
                const verifyResponse = await userService.startPhoneNumberVerification();
                if (verifyResponse.status === 200) {
                    this.enterCodeDialog("sms");
                } else {
                    f7.dialog.alert(this.$t('app.dialog.error.phone-verification-failed'), this.$t('app.dialog.error.title'));
                }
            },
            async startEmailVerification() {
                console.log("STARTING EMAIL VERIFICATION PROCESS ...");
                const verifyResponse = await userService.startEmailVerification();
                if (verifyResponse.status === 200) {
                    this.confirmEmail();
                } else {
                    f7.dialog.alert(this.$t('app.dialog.error.email-verification-failed'), this.$t('app.dialog.error.title'));
                }
            },
            enterCodeDialog(type) {
                var codeDialogText = '';
                switch(type) {
                    case "sms":
                        codeDialogText = this.$t('account.sheet.personaldata.dialog.enterCodeSMS');
                        break;
                    default:
                        codeDialogText = this.$t('app.dialog.success.enterCode');
                        break;
                }
                this.checkCodeDialog = f7.dialog.create({
                    text: codeDialogText,
                    content: `
                        <div class="dialog-input">
                            <div style="align-items: center;">
                                <input type="text" maxlength="6" pattern="[0-9]*" inputmode="numeric" id="code" class="code-input" />
                            </div>
                        </div>
                    `,
                    buttons: [
                        {
                            text: this.$t('app.dialog.cancel'),
                            onClick: () => {
                                // Cancel action
                            }
                        },
                        {
                            text: this.$t('app.dialog.ok'),
                            onClick: async () => {
                                const code = document.getElementById('code').value;
                                this.checkCode(code, type);
                            }
                        }
                    ],
                }).open();

                this.checkCodeDialog.on('opened', () => {
                    this.addInputListener();
                });
            },
            async checkCode(code, type) {
                switch(type) {
                    case "sms":
                        const responseVerifySMS = await userService.checkPhoneNumberVerificationCode({ code: code });
                        console.log("response checkPhoneNumberVerificationCode: ", responseVerifySMS)
                        if (responseVerifySMS.status === 200) {
                            if (responseVerifySMS.data.verified) {
                                console.log("PHONE VERIFICATION SUCCESSFUL ...");
                                this.phone_verified = this.phone_unverified;
                                this.phone_unverified = null;
                                this.showToastSuccess(this.$t('app.dialog.success.phone'));
                                this.emitter.emit('show-verify-toast');
                            } else {
                                f7.dialog.alert(this.$t('app.dialog.error.wrong-code'), this.$t('app.dialog.error.title'));
                            }
                        } else {
                            f7.dialog.alert(this.$t('app.dialog.error.wrong-code'), this.$t('app.dialog.error.title'));
                        }
                        break;
                    default:
                        break;
                }
            },
            addInputListener() {
                const inputElement = document.getElementById('code');
                const okButton = this.checkCodeDialog.el.querySelector('.dialog-button:nth-child(2)');

                okButton.classList.add('disabled');
                okButton.disabled = true;

                if (inputElement) {
                    inputElement.focus();
                    inputElement.addEventListener('input', () => {
                        const isFilled = inputElement.value.length === 6;
                        okButton.classList.toggle('disabled', !isFilled);
                        okButton.disabled = !isFilled;
                    });
                }
            },
            confirmEmail() {
                const dialog = f7.dialog.confirm(
                    this.$t('app.dialog.request'),
                    async () => {
                        const response = await userService.getUserData();
                        if (response.status === 200) {
                            if (response.data.email_is_verified) {
                                this.email_verified = this.email_unverified;
                                this.email_unverified = null;
                                this.showToastSuccess(this.$t('app.dialog.success.mail'));
                                this.emitter.emit('show-verify-toast');
                            }  else {
                                f7.dialog.alert(this.$t('app.dialog.error.not-verified-email'), this.$t('app.dialog.error.title'));
                            }
                        } else {
                            f7.dialog.alert(this.$t('app.dialog.error.not-verified-email'), this.$t('app.dialog.error.title'));
                        }
                    }
                );

                // Wait for the dialog to be rendered
                this.$nextTick(() => {
                    const buttons = $(".dialog .dialog-button");
                    const okButton = buttons[buttons.length - 1];
                    if (okButton) {
                        okButton.classList.add('disabled');
                        okButton.disabled = true;

                        const okText = this.$t('app.dialog.ok');
                        let secondsLeft = Math.floor(this.dismissOK / 1000);
                        const originalText = okButton.textContent;
                        okButton.textContent = `${okText} (${secondsLeft})`;

                        const interval = setInterval(() => {
                            secondsLeft -= 1;
                            if (secondsLeft > 0) {
                                okButton.textContent = `${okText} (${secondsLeft})`;
                            } else {
                                clearInterval(interval);
                                okButton.classList.remove('disabled');
                                okButton.disabled = false;
                                okButton.textContent = okText;
                            }
                        }, 1000);
                    }
                });
            },
            showToastSuccess(text) {
                f7.toast.show({
                    text: text,
                    icon: '<i class="f7-icons">checkmark_alt_circle</i>',
                    position: 'center',
                    closeTimeout: 2000,
                });
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
        },
        unmounted() {
        }
    };
</script>