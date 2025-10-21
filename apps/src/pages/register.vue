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
      
        <NavBar ref="navBar" :title="title" :showSearch="false" :showIcons="false"/>
        
        <f7-page :page-content="true">
            <div class="full-height-div">
                <div class="container">
                    <div class="box box-top">
                        <div class="login-background">
                            <f7-block>
                                <div class="avatar-container">
                                    <div 
                                        class="avatar" 
                                        :style="{ backgroundImage: `url(${imageTemp})` }"
                                    ></div>
                                    <div class="avatar-edit">
                                        <f7-link @click="editProfileImage" data-cy="register-avatar-lnk"><f7-icon ios="f7:pencil" md="material:edit"></f7-icon></f7-link>
                                    </div>
                                </div>
                                <form @submit.prevent @reset.prevent>
                                    <f7-list strong-ios dividers-ios inset>
                                        <f7-list-input 
                                            :label="this.$t('register.name.label')" 
                                            type="text" 
                                            :placeholder="this.$t('register.name.placeholder')" 
                                            :error-message="this.$t('register.name.error')"
                                            :error-message-force="v$.name.$error"
                                            :value="name"
                                            @input="name = $event.target.value"
                                            @blur="v$.name.$touch"
                                            v-model:value="name"
                                            autocomplete="name"
                                            data-cy="register-name-fld"
                                        ></f7-list-input>
                                        <f7-list-input 
                                            :label="this.$t('register.email.label')" 
                                            type="email" 
                                            :placeholder="this.$t('register.email.placeholder')" 
                                            :error-message="error_email"
                                            :error-message-force="v$.email.$error"
                                            :value="email"
                                            @input="email = $event.target.value"
                                            @blur="v$.email.$touch"
                                            v-model:value="email"
                                            autocomplete="email"
                                            data-cy="register-email-fld"
                                        ></f7-list-input>

                                        <f7-list-input
                                            :label="this.$t('register.phone.label')"
                                            type="text"
                                            :placeholder="this.$t('register.phone.placeholder')"
                                            :error-message="v$.phone.$errors[0]?.$message"
                                            :error-message-force="v$.phone.$error"
                                            :value="phone"
                                            @input="phone = $event.target.value"
                                            @blur="v$.phone.$touch"
                                            v-model:value="phone"
                                            autocomplete="tel"
                                            data-cy="register-phone-fld"
                                        ></f7-list-input>
                                    </f7-list>

                                    <f7-list strong-ios dividers-ios inset style="margin-top: 10px; margin-bottom: 10px;">
                                        <f7-list-input 
                                            :label="this.$t('register.password.label')" 
                                            type="password" 
                                            :placeholder="this.$t('register.password.placeholder')" 
                                            :error-message="this.$t('register.password.error')"
                                            :error-message-force="v$.password.$error"
                                            :value="password"
                                            @input="password = $event.target.value"
                                            @blur="v$.password.$touch"
                                            v-model:value="password"
                                            autocomplete="new-password"
                                            data-cy="register-pwd-fld"
                                        ></f7-list-input>

                                        <f7-list-input
                                            :label="this.$t('register.passwordrepeat.label')"
                                            type="password"
                                            :placeholder="this.$t('register.passwordrepeat.placeholder')"
                                            :error-message="this.$t('register.passwordrepeat.error')"
                                            :error-message-force="v$.password_repeat.$error"
                                            :value="password_repeat"
                                            @input="password_repeat = $event.target.value"
                                            @blur="v$.password_repeat.$touch"
                                            v-model:value="password_repeat"
                                            autocomplete="new-password"
                                            data-cy="register-pwd-repeat-fld"
                                        ></f7-list-input>

                                        <f7-list-input 
                                            :label="this.$t('register.campusrelation.label')" 
                                            type="select" 
                                            :error-message="this.$t('register.campusrelation.error')"
                                            :error-message-force="v$.campusRelation.$error"
                                            v-model:value="campusRelation"
                                            data-cy="register-relation-fld"
                                        >
                                            <option value="" disabled>
                                                {{ this.$t('register.campusrelation.placeholder') }}
                                            </option>
                                            <option 
                                                v-for="relation in campusRelations"
                                                :key="relation.id"
                                                :value="relation.id">
                                            {{ relation.string }}
                                            </option>
                                        </f7-list-input>
                                        <f7-list-item :title="this.$t('register.terms.label')">
                                            <template #media>
                                                <f7-button data-cy="register-terms-btn" href="#" popup-open=".terms-popup" small><f7-icon f7="info_circle" /></f7-button>
                                            </template>
                                            <template #after>
                                                <f7-toggle data-cy="register-terms-tgl" v-model:checked="termsChecked" />
                                            </template>
                                        </f7-list-item>
                                    </f7-list>

                                    <f7-list inset style="margin-top: 10px; margin-bottom: 10px;">
                                        <f7-list-item 
                                            :title="this.$t('register.faceid.title')" 
                                            :footer="this.$t('register.faceid.footer')"
                                        >
                                            <template #after>
                                                <f7-toggle data-cy="register-faceid-tgl" v-model:checked="faceIDLogin"/>
                                            </template>
                                        </f7-list-item>
                                    </f7-list>

                                    <f7-button data-cy="register-signup-btn" type="submit" large fill @click="register"><f7-icon ios="f7:checkmark_seal_fill" md="material:verified"></f7-icon>&nbsp;{{ this.$t('register.button.registration') }}</f7-button>
                                </form>
                            </f7-block>
                        </div>
                    </div>
                </div>
            </div>

            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" :tabActive="tabActive"/>

        <f7-popup v-model:opened="termsOpen" class="terms-popup">
            <f7-page>
                <f7-navbar :title="this.$t('register.terms.sheet.title')">
                    <f7-nav-right>
                        <f7-link popup-close data-cy="register-terms-popupclose-lnk">{{ this.$t('register.terms.sheet.link') }}</f7-link>
                    </f7-nav-right>
                </f7-navbar>
                <Legal ref="terms" document="terms" />
            </f7-page>
        </f7-popup>
    </f7-page>

    <ImagePicker ref="imagePicker"/>
</template>

<script>
  import { getDevice }  from 'framework7';
  import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link, f7ListInput } from 'framework7-vue';

  import ImagePicker from '../components/imagePicker.vue';
  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';
  import Legal from '../components/legal.vue';

  import useVuelidate from '@vuelidate/core'
  import { required, minLength, sameAs, email, helpers } from '@vuelidate/validators';
  const phoneNumber = (value) => /^[0-9\s\+\-\(\)]+$/.test(value);
  import placeholderImage from "../assets/placeholder/images/profileImagePlaceholder.png";

  import userService from '../services/userService';
  import messageService from '../services/messageService';
  import { customRound } from '../js/utilities/utils';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Tabs,
        f7Tab,
        f7Link,
        f7ListInput,
        NavBar,
        ToolBar,
        ImagePicker,
        Legal
    },
    data() {
        return {
            device: getDevice(),
            title: this.$t('register.title'),
            tabActive: 4,
            actionsToPopover: null,
            name: '',
            email: '',
            phone: '',
            password: '',
            password_repeat: '',
            campusRelation: '',
            termsChecked: false,
            termsOpen: false,
            error_email: this.$t('register.email.error'),
        };
    },
    setup () {
        return { v$: useVuelidate() }
    },
    validations() {
        return {
            name: {
                required
            },
            phone: {
                required: helpers.withMessage(this.$t('register.phone.required'), required),
                phoneNumber: helpers.withMessage(this.$t('register.phone.invalid'), phoneNumber)
            },
            email: {
                required,
                email
            },
            password: {
                required,
                minLength: minLength(8)
            },
            password_repeat: {
                sameAsPassword: sameAs(this.password)
            },
            campusRelation: {
                required
            }
        }
    },
    computed: {
        pushToken() {
            return this.$store.getters.getPushToken;
        },
        userID: {
            get() {
                return this.$store.getters.getUserID;
            },
            set(v) {
                this.$store.dispatch('setUserID', { id: v });
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
        email_unverified: {
            get() {
                return this.$store.getters.getUserEmailUnverified;
            },
            set(v) {
                this.$store.dispatch('setUserEmailUnverified', { email: v });
            }
        },
        imageTemp: {
            get() {
                let image = this.$store.getters.getUserImageTempUrl;
                if (!image) return placeholderImage;
                // If it's a DataURL, return as-is
                if (image.startsWith('data:')) return image;
                // Otherwise, append timestamp for cache busting
                return image + '?t=' + this.$store.getters.getUserUpdatedImageAt;
            },
            set(v) {
                this.$store.dispatch('setUserImageTempUrl', { imageURL: v });
            }
        },
        imageTempBase64: {
            get() {
                return this.$store.getters.getUserImageTempBase64;
            },
            set(v) {
                this.$store.dispatch('setUserImageTempBase64', { imageBase64: v });
            }
        },
        campusRelations: {
            get() {
                return this.$store.getters.getCampusRelations;
            },
            set(v) {
                this.$store.dispatch('setCampusRelations', { relations: v })
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
        appLanguage() {
            return this.$store.getters.getAppLanguage;
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
        }
    },
    mounted() {
        f7ready(() => {
            this.imageTempBase64 = null;
            this.imageTemp = null;
            this.setCampusRelations();
        })
    },
    methods: {
        async validateEmail(value) {
            if (value === '') {
                this.error_email = this.$t('register.email.error');
                return true;
            }
            const credentials = {
                email: value
            };
            const response = await userService.validateEmail(credentials);
            if (response.status === 409) {
                this.error_email = this.$t('register.email.inUseError');
                return true;
            } else if (response.status === 400) {
                this.error_email = this.$t('register.email.notValidError');
                return true;
            } else {
                this.error_email = '';
                return false;
            }
        },
        async setCampusRelations() {
            console.log("SET CAMPUS RELATIONS...")
            const lang = this.appLanguage;
            let result = await userService.getCampusRelations();
            const categories = result.categories;

            let CAMPUS_RELATIONS = categories.map(category => ({
                id: Number(category.id),
                value: category.name[lang],
                string: category.description[lang]
            }));
            this.campusRelations = CAMPUS_RELATIONS;
        },
        async register() {
            try {
                this.v$.$touch();
                if (this.v$.$invalid) {
                    return;
                }

                if (!this.termsChecked) {
                    f7.dialog.alert(this.$t('register.terms.error'), this.$t('app.dialog.error.title'));
                    return;
                }

                let emailIsUnique = await this.validateEmail(this.email.toLowerCase());
                if (emailIsUnique) {
                    f7.dialog.alert(this.error_email, this.$t('app.dialog.error.title'));
                    return; 
                }

                const credentials = {
                    name: this.name,
                    mobile_phone_number: this.phone,
                    email: this.email.toLowerCase(),
                    password: this.password,
                    category_id: this.campusRelation
                };
                const response = await userService.register(credentials);
                if (response.status === 200) {
                    console.log("USER REGISTERED SUCCESSFULLY! ");
                    this.userID = response.data.userID;
                    await this.login();
                    if (this.imageTempBase64) {
                        this.uploadUserImage();
                    }
                    f7.view.current.router.navigate('/account', { history: false, clearPreviousHistory: true, ignoreCache: true, animate: true, transition: 'f7-flip' });
                } else {
                    f7.dialog.alert(this.$t('app.dialog.error.text'), this.$t('app.dialog.error.title'));
                }
            } catch (error) {
                console.log("error: ", error)
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
        },
        takeImage() {
            this.$refs.imagePicker.takeImage(false);
        },
        getImage() {
            this.$refs.imagePicker.getImage(false);
        },
        uploadUserImage() {
            this.$refs.imagePicker.uploadUserImage();
        },
        async login() {
            try {
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

                    this.phone_unverified = response.data.user.mobile_number_unverified;
                    this.email_unverified = response.data.user.email;

                    this.getMessages();
                    this.registerPushToken();
                    this.getUserStatistics();
                }
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
        async registerPushToken() {
            if (!this.device.cordova) return;       // Are we on device?
            if (!this.pushToken) return;                 // Is there a push token yet?

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
        }
    },
  };
</script>