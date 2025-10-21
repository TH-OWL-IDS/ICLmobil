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
              style="min-height: 460px" 
              swipe-to-close 
              push 
              backdrop 
              :close-by-backdrop-click="true" 
              :close-by-outside-click="false" 
              class="userData">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <f7-toolbar class="sheet-toolbar-pagecolor">
            <div class="left sheet-title">
                {{ this.$t('account.sheet.personaldata.title') }}
            </div>
            <div class="right">
                <f7-link @click="closeSheet">
                    <f7-icon style="color: #ccc !important;" ios="f7:multiply_circle_fill" md="material:cancel"></f7-icon>
                </f7-link>
            </div>
        </f7-toolbar>

        <f7-page :page-content="true">
            <f7-block>
                <div class="avatar-wrapper">
                    <div class="avatar-container">
                        <div 
                            class="avatar" 
                            :style="{ backgroundImage: `url(${image})` }"
                        ></div>
                        <div class="avatar-edit">
                            <f7-link @click="editProfileImage"><f7-icon ios="f7:pencil" md="material:edit"></f7-icon></f7-link>
                        </div>
                    </div>
                </div>
            </f7-block>
            
            <f7-block>
                <f7-list strong-ios dividers-ios>
                    <f7-list-item :title="this.$t('account.sheet.personaldata.name')" :footer="name">
                        <template #after>
                            <f7-link @click="openPrompt('name')">
                                <f7-icon ios="f7:pencil" md="material:edit"></f7-icon>
                            </f7-link>
                        </template>
                    </f7-list-item>
                    <f7-list-item :title="this.$t('account.sheet.personaldata.phone')" :footer="phone">
                        <template #after>
                            <f7-link @click="openPrompt('phone')">
                                <f7-icon ios="f7:pencil" md="material:edit"></f7-icon>
                            </f7-link>
                        </template>
                    </f7-list-item>
                    <f7-list-item :title="this.$t('account.sheet.personaldata.email')" :footer="email">
                        <template #after>
                            <f7-link @click="openPrompt('email')">
                                <f7-icon ios="f7:pencil" md="material:edit"></f7-icon>
                            </f7-link>
                        </template>
                    </f7-list-item>
                    <f7-list-item :title="this.$t('account.sheet.personaldata.password')" :footer="hiddenPassword">
                        <template #after>
                            <f7-link @click="openPrompt('password')">
                                <f7-icon ios="f7:pencil" md="material:edit"></f7-icon>
                            </f7-link>
                        </template>
                    </f7-list-item>
                </f7-list>
            </f7-block>
        </f7-page>
    </f7-sheet>

    <ImagePicker ref="imagePicker"/>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';
  import $ from "dom7";
  import ImagePicker from './imagePicker.vue';

  import userService from '../services/userService';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Link,
        ImagePicker
    },
    data() {
        return {
            hiddenPassword: "***********",
            actionsToPopover: null,
            checkCodeDialog: null,
            dismissOK: 8000
     };
    },
    computed: {
        image: {
            get() {
                this.checkUserImage();
                return this.$store.getters.getUserImage + '?t=' + this.$store.getters.getUserUpdatedImageAt;
            },
            set(v) {
                this.$store.dispatch('setUserImage');
                this.$store.dispatch('setUserImageUpdatedAt', { updated: new Date().getTime() });
            }
        },
        name: {
            get() {
                return this.$store.getters.getUserName;
            },
            set(v) {
                this.$store.dispatch('setUserName', { name: v });
            }
        },
        phone: {
            get() {
                let phone = this.$store.getters.getUserPhone;
                return phone ? phone : this.phone_unverified;
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
        email: {
            get() {
                let email = this.$store.getters.getUserEmail;
                return email ? email : this.email_unverified;
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
        token() {
            return this.$store.getters.getUserToken;
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    methods: {
        init() {
            console.log("SHEET PERSONAL DATA OPENED")
        },
        onClose() {
            console.log("SHEET CLOSING")
        },
        async checkUserImage() {
            let response = await userService.checkUserImage(this.$store.getters.getUserID);
            if (response.status === 404) {
                this.$store.dispatch('setUserImageDefault');
            }
        },
        openPrompt(editField) {
            this.sendHapticFeedback('CONFIRM', 'ImpactMedium');
            switch(editField) {
                case "name":
                    f7.dialog.prompt(this.$t('account.sheet.personaldata.dialog.changename'), async (name) => {
                        if (name === ''){
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('register.name.error'), this.$t('app.dialog.error.title'));
                            return;
                        }
                        const response = await userService.updateUser({ name: name });
                        if (response.status === 200) {
                            this.sendHapticFeedback('CONFIRM', 'Success');
                            this.name = name;
                        } else {
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('app.dialog.error.text'), this.$t('app.dialog.error.title'));
                        }
                    });
                    break;
                case "phone":
                    f7.dialog.prompt(this.$t('account.sheet.personaldata.dialog.changephone'), async (phone) => {
                        if (phone === ''){
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('register.phone.error'), this.$t('app.dialog.error.title'));
                            return;
                        }
                        // Update the mobile number in backend
                        const updateResponse = await userService.updateUser({ mobile_number: phone });
                        if (updateResponse.status === 200) {
                            this.sendHapticFeedback('CONFIRM', 'Success');
                            this.phone_unverified = phone;
                            // Start backend verification process
                            const verifyResponse = await userService.startPhoneNumberVerification();
                            if (verifyResponse.status === 200) {
                                this.enterCodeDialog("sms");
                            } else {
                                f7.dialog.alert(this.$t('app.dialog.error.phone-verification-failed'), this.$t('app.dialog.error.title'));
                            }
                        } else {
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('app.dialog.error.phone-verification-failed'), this.$t('app.dialog.error.title'));
                        }
                    });
                    break;
                case "email":
                    f7.dialog.prompt(this.$t('account.sheet.personaldata.dialog.changeemail'), async (email) => {
                        if (email === ''){
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('register.email.error'), this.$t('app.dialog.error.title'));
                            return;
                        }
                        // Update the email in backend
                        const updateResponse = await userService.updateUser({ email: email });
                        if (updateResponse.status === 200) {
                            this.sendHapticFeedback('CONFIRM', 'Success');
                            this.email_unverified = email;
                            // Start backend verification process
                            const verifyResponse = await userService.startEmailVerification();
                            if (verifyResponse.status === 200) {
                                this.confirmEmail();
                            } else {
                                f7.dialog.alert(this.$t('app.dialog.error.email-verification-failed'), this.$t('app.dialog.error.title'));
                            }
                        } else {
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('app.dialog.error.email-verification-failed'), this.$t('app.dialog.error.title'));
                        }
                    });
                    break;
                case "password":
                    f7.dialog.password(this.$t('account.sheet.personaldata.dialog.changepassword1'), async (oldPasswordEntered) => {
                        const checkPasswordResponse = await userService.checkPassword({ password: oldPasswordEntered });
                        if (checkPasswordResponse.status === 200) {
                            this.sendHapticFeedback('CONFIRM', 'Success');
                            f7.dialog.password(this.$t('account.sheet.personaldata.dialog.changepassword2'), async (newPassword) => {
                                f7.dialog.password(this.$t('account.sheet.personaldata.dialog.changepassword3'), async (newPasswordRepeat) => {
                                    if (newPassword !== newPasswordRepeat) {
                                        this.sendHapticFeedback('REJECT', 'Error');
                                        f7.dialog.alert(this.$t('account.sheet.personaldata.dialog.changepassword4'), this.$t('app.dialog.error.title'));
                                    } else {
                                        const response = await userService.updateUser({ password: newPassword });
                                        if (response.status === 200) {
                                            this.sendHapticFeedback('CONFIRM', 'Success');
                                            f7.dialog.alert(this.$t('account.sheet.personaldata.dialog.changepassword5'));
                                        } else {
                                            this.sendHapticFeedback('REJECT', 'Error');
                                            f7.dialog.alert(this.$t('app.dialog.error.servertext'), this.$t('app.dialog.error.title'));
                                            return;
                                        }
                                    }
                                });
                            });
                        } else {
                            this.sendHapticFeedback('REJECT', 'Error');
                            f7.dialog.alert(this.$t('account.sheet.personaldata.dialog.changepassword6'), this.$t('app.dialog.error.title'));
                        }
                    });
                    break;
            }

        },
        confirmEmail() {
            const dialog = f7.dialog.confirm(this.$t('app.dialog.request'), async () => {
                const response = await userService.getUserData();
                if (response.status === 200) {
                    if (response.data.email_is_verified) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        this.email = this.email_unverified;
                        this.email_unverified = null;
                        this.showToastSuccess(this.$t('app.dialog.success.mail'));
                    }  else {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.not-verified-email'), this.$t('app.dialog.error.title'));
                    }
                } else {
                    this.sendHapticFeedback('REJECT', 'Error');
                    f7.dialog.alert(this.$t('app.dialog.error.not-verified-email'), this.$t('app.dialog.error.title'));
                }
            });

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
                    if (responseVerifySMS.status === 200) {
                        if (responseVerifySMS.data.verified) {
                            this.phone = this.phone_unverified;
                            this.phone_unverified = null;
                            this.showToastSuccess(this.$t('app.dialog.success.text'));
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
        editProfileImage() {
            this.actionsToPopover = f7.actions.create({
                buttons: [
                    [
                        { 
                            text: this.$t('app.dialog.actions.userimage.title'), 
                            label: true 
                        },
                        {
                            text: this.$t('app.dialog.actions.userimage.take'),
                            onClick: () => {
                                this.takeImage();
                            },
                        },
                        { 
                            text: this.$t('app.dialog.actions.userimage.get'),
                            onClick: () => {
                                this.getImage();
                            }
                         },
                    ],
                    [{ 
                        text: 'Cancel', 
                        color: 'red' 
                    }],
                ],
                convertToPopover: false
            });
            this.actionsToPopover.open();
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
        },
        takeImage() {
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            this.$refs.imagePicker.takeImage(true);
        },
        getImage() {
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactLight");
            this.$refs.imagePicker.getImage(true);
        },
        closeSheet() {
            this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
            f7.sheet.close('.userData');
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