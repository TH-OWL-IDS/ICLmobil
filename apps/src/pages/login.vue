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
      
        <NavBar ref="navBar" :large="true" :title="title" :showSearch="false" :showIcons="false"/>
        
        <f7-page :page-content="true">

            <div class="full-height-div">
                <div class="container">
                    <div class="box box-top">
                        <div class="login-background">
                            <f7-block>
                                <div class="login-title title-large">
                                    <div v-html="this.$t('login.header')"></div>
                                </div>

                                <form @submit.prevent @reset.prevent>
                                    <f7-list strong-ios dividers-ios inset>
                                        <f7-list-input 
                                            :label="this.$t('login.email.label')" 
                                            type="email" 
                                            :placeholder="this.$t('login.email.placeholder')"
                                            :error-message="this.$t('login.email.error')"
                                            :error-message-force="v$.email.$error"
                                            :value="email"
                                            @input="email = $event.target.value"
                                            @blur="v$.email.$touch"
                                            v-model:value="email"
                                            data-cy="login-email-fld"
                                        >
                                            <template #media>
                                                <i class="icon f7-icons">envelope</i>
                                            </template>
                                        </f7-list-input>

                                        <f7-list-input
                                            :label="this.$t('login.password.label')"
                                            type="password"
                                            :placeholder="this.$t('login.password.placeholder')"
                                            :error-message="this.$t('login.password.error')"
                                            :error-message-force="v$.password.$error"
                                            :value="password"
                                            @input="password = $event.target.value"
                                            @blur="v$.password.$touch"
                                            v-model:value="password"
                                            @keydown.enter="loginBlur"
                                            data-cy="login-password-fld"
                                        >
                                            <template #media>
                                                <i class="icon f7-icons">ellipsis</i>
                                            </template>
                                        </f7-list-input>
                                        <li>
                                            <div class="item-content">
                                                <div class="item-inner">
                                                    <div class="item-media">
                                                        <i class="icon f7-icons">lock</i>
                                                    </div>
                                                    <div class="login-faceid">
                                                        {{ this.$t('login.faceid.title') }}
                                                    </div>
                                                    <div class="item-after">
                                                        <f7-toggle data-cy="login-faceid-tgl" v-model:checked="faceIDLogin"/>
                                                    </div>
                                                </div>
                                            </div>
                                        </li>
                                    </f7-list>

                                    <div class="button-wrapper">
                                        <f7-button large fill @click="login" data-cy="login-login-btn"><f7-icon ios="f7:person_crop_circle_badge_checkmark" md="material:account_circle"></f7-icon>&nbsp;{{ this.$t('login.button.login') }}</f7-button>
                                    </div>
                                </form>

                                <div class="button-wrapper">
                                    <f7-link @click="forgotPassword" class="link-large" data-cy="login-pwd-recover-lnk">
                                        <f7-icon ios="f7:lock_fill" md="material:lock"  style="vertical-align: baseline !important;"></f7-icon>
                                        {{ this.$t('login.link.forgot-password') }}
                                    </f7-link>
                                </div>

                                <div class="login-hint">
                                    {{ this.$t('login.hint') }}
                                </div>

                                <f7-link @click="register" class="link-large" data-cy="login-register-lnk">{{ this.$t('login.link.register') }}</f7-link>

                                <div class="login-hint-small">
                                    {{ this.$t('login.hintsmall') }}
                                </div>
                            </f7-block>
                        </div>
                    </div>
                </div>
            </div>

            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" :tabActive="tabActive"/>

        <Recover/>
    </f7-page>
</template>

<script>
  import { getDevice }  from 'framework7';
  import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import useVuelidate from '@vuelidate/core'
  import { required, email } from '@vuelidate/validators';
  
  import userService from '../services/userService';
  import messageService from '../services/messageService';
  import { customRound } from '../js/utilities/utils';

  import Recover from '../components/recover.vue';
  
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
        Recover
    },
    data() {
        return {
            device: getDevice(),
            title: this.$t('login.title'),
            tabActive: 4,
            email: '',
            password: ''
     };
    },
    setup () {
        return { v$: useVuelidate({ $scope: false }) }
    },
    validations() {
        return {
            email: {
                required,
                email
            },
            password: {
                required
            }
        }
    },
    computed: {
        pushToken() {
            return this.$store.getters.getPushToken;
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
        faceIDLogin: {
            get() {
                return this.$store.getters.getFaceIDLogin;
            },
            set(v) {
                this.$store.dispatch('setFaceIDLogin', { faceid: v });
            }
        },
        messages: {
            get() {
                return this.$store.getters.getMessages(this.$i18n.locale);
            },
            set(v) {
                this.$store.dispatch('setMessages', { messages: v });
            }
        },
        userStatistics: {
            get() {
                return this.$store.getters.getUserStatistics;
            },
            set(v) {
                this.$store.dispatch('setUserStatistics', { statistics: v });
                this.dispatchWalletData(v);
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
    },
    mounted() {
        f7ready(() => {
            console.log("WE ARE ON DEVICE: ", this.device.cordova);
        })
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
        async login() {
            try {
                this.v$.$touch();
                if (this.v$.$invalid)
                    return;
                
                const credentials = {
                    email: this.email.toLowerCase(),
                    password: this.password
                };
                const response = await userService.login(credentials);
                if (response.status === 200) {
                    this.$store.dispatch('setUserToken', { token: response.data.token });

                    this.RegisterBiometricSecret(response.data.token);

                    this.$store.dispatch('setUserID', { id: response.data.user.userid })
                    this.$store.dispatch('setUserName', { name: response.data.user.name });
                    this.$store.dispatch('setUserImage');
                    this.$store.dispatch('setUserImageUpdatedAt', { updated: new Date().getTime() });

                    if (response.data.user.mobile_number_is_verified) {
                        console.log("PHONE VERIFIED, SET AS VERIFIED...");
                        this.phone_verified = response.data.user.mobile_number_verified;
                        this.phone_unverified = null;
                    } else {
                        console.log("PHONE UNVERIFIED, SET AS UNVERIFIED...");
                        this.phone_verified = null;
                        this.phone_unverified = response.data.user.mobile_number_unverified;
                    }

                    if (response.data.user.email_is_verified) {
                        console.log("EMAIL VERIFIED, SET AS VERIFIED...");
                        this.email_verified = response.data.user.email;
                        this.email_unverified = null;
                    }  else {
                        console.log("EMAIL UNVERIFIED, SET AS UNVERIFIED...");
                        this.email_verified = null;
                        this.email_unverified = response.data.user.email;
                    }

                    this.updatePoolLinkStatus();
                    this.getMessages();
                    this.registerPushToken();
                    this.getUserStatistics();

                    f7.view.current.router.navigate('/account', { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: 'f7-flip' });

                } else if (response.status === 401) {
                    if (response.data.reason === 'unknown_email') {
                        f7.dialog.alert(this.$t('app.dialog.error.wrong-email'), this.$t('app.dialog.error.title'));
                    } else if (response.data.reason === 'wrong_password') {
                        f7.dialog.alert(this.$t('app.dialog.error.wrong-password'), this.$t('app.dialog.error.title'));
                    }
                } else {
                    f7.dialog.alert(this.$t('app.dialog.error.text'), this.$t('app.dialog.error.title'));
                }
            } catch (err) {
                console.log(err)
            }
        },
        forgotPassword() {
            try {
                f7.dialog.prompt(this.$t('login.dialog.prompt-text'), async (email) => {
                    email = email.toLowerCase();
                    const data = {
                        email: email
                    };
                    const response = await userService.recover(data);
                    if (response.status === 200) {
                        this.openRecover(email);
                    } else if (response.status === 409) {
                        f7.dialog.alert(this.$t('app.dialog.error.wrong-email'), this.$t('app.dialog.error.title'));
                    } else {
                        f7.dialog.alert(this.$t('app.dialog.error.text'), this.$t('app.dialog.error.title'));
                    }
                });
            } catch (err) {
                console.log(err)
            }
        },
        async getMessages() {
            const response = await messageService.getMessages();
            if (response.status === 200) {
                console.log("GETTING USER MESSAGES: ", response.data.items);
                this.messages = response.data.items;
            }
        },
        RegisterBiometricSecret(token) {
            if (this.device.cordova) {
                console.log("REGISTER BIOMETRIC DATA ...");
                Fingerprint.registerBiometricSecret({
                    description: "User Token",
                    secret: token,
                    invalidateOnEnrollment: true,
                    disableBackup: true,
                }, function(result) {
                    console.log("Token erfolgreich mit biometrischer Authentifizierung gespeichert", result);
                }, function(error) {
                    console.error("Fehler beim Speichern des Tokens", error);
                });
            }
        },
        register() {
            f7.view.current.router.navigate('/register', { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: 'f7-fade' });
        },
        loginBlur(e) {
            e.target.blur();
            this.login();
        },
        async registerPushToken() {
            if (!this.device.cordova) return;       // Are we on device?
            if (!this.pushToken) return;            // Is there a push token yet?

            console.log("REGISTER PUSH TOKEN: ", this.pushToken);

            let pushSystem = null;
            let device = null;
            let deviceModel = null;
            let deviceOS = this.device.os;
            let deviceOSVersion = this.device.osVersion;

            if (this.device.ios) {
                pushSystem = "apple";
                if (this.device.iphone) { device = "iphone" }
                if (this.device.ipod) { device = "ipod" }
                if (this.device.ipad) { device = "ipad" }
            } else if (this.device.android) {
                pushSystem = "android";
                device = "android";
            }
            deviceModel = device + " - " + deviceOS + " " + deviceOSVersion;

            let data = 
            {
                "push_system": pushSystem,
                "device_model": deviceModel,
                "token": this.pushToken
            }
            let response = await messageService.registerPushToken(data);
            if (response.status === 200) {
                console.log("PUSH TOKEN REGISTERED SUCCESSFULLY!")
            } else {
                console.log("PUSH TOKEN REGISTRATION FAILED")
            }
        },
        async getUserStatistics() {
            try {
                const response = await userService.getUserStatistics();
                if (response.status === 200) {
                    this.userStatistics = response.data;
                } else {
                    console.log("ERROR: ", response.data.error);
                }
            } catch(err) {
                console.log("ERROR: ", err);
            }
        },
        dispatchWalletData(data) {
            const tons = (data.completed_bookings_co2e_reduction_g / 1000).toFixed(1);
            const hours = Math.round(data.completed_bookings_duration_hour);
            const distance = Math.round(data.completed_bookings_distance_km);

            this.$store.dispatch('setRanking', { ranking: this.reparseLeaderboard(data.leaderboard) });
            this.$store.dispatch('setExperienceLevel', { experienceLevel: data.rank });
            this.$store.dispatch('setExperiencePoints', { experiencePoints: data.points });
            this.$store.dispatch('setExperienceScore', { experienceScore: data.experience });
            this.$store.dispatch('setExperienceScore', { experienceScore: data.experience });
            this.$store.dispatch('setTotalEmmisions', { totalEmmisions: tons });
            this.$store.dispatch('setTotalDuration', { totalDuration: hours });
            this.$store.dispatch('setTotalDistance', { totalDistance: distance });
            this.$store.dispatch('setTotalRides', { totalRides: data.completed_bookings_count });

            let statistics = [customRound(data.booking_percentage_per_mode.scooter),
                              customRound(data.booking_percentage_per_mode.bike),
                              customRound(data.booking_percentage_per_mode.car),
                              customRound(data.booking_percentage_per_mode.pt),
                              customRound(data.booking_percentage_per_mode.walk)];
            this.$store.dispatch('setStatistics', { statistics: statistics });
        },
        reparseLeaderboard(data) {
            return data.map((item, index) => ({
                id: index,
                name: item[0],
                points: item[2],
                rank: item[1]
            }));
        },
        openRecover(email) {
            this.emitter.emit('set-recover-email', email);
            f7.sheet.open('.recover');
        }
    },
  };
</script>

<style scoped>
    .button-wrapper {
        padding-bottom: 20px;
    }
    .link-wrapper {
        padding-bottom: 30px;
    }
</style>