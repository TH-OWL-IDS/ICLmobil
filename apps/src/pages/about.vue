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

            <Logo ref="logo"/>
            
            <f7-block>
                <div class="about-header text-align-center block-title block-title-large">
                    ICL-Mobile App v{{ appVersion }}
                </div>

                <div class="about-text">
                    Das Projekt ICLMobil umfasst eine Vielzahl von Maßnahmen, die darauf abzielen, den motorisierten Individualverkehr auf alternative Verkehrsmittel wie den öffentlichen Nahverkehr, Fahrrad und Scooter zu lenken und Emissionen zu reduzieren<br />
                    <br/>
                    Ein zentraler Bestandteil des Projekts ist die ICL-Mobile App.<br />
                    <br/>
                    Diese App soll eine transparente Darstellung und Nutzung aller Mobilitätsangebote in Lemgo ermöglichen und den Austausch über nachhaltige Mobilitätskonzepte fördern. Neben der Verbesserung der ÖPNV-Strukturen und Sharingmöglichkeiten von E-Scootern und E-Bikes sind auch insbesondere innovative Lösungen für Austauschplattformen zur Bildung von privaten Mitfahrgelegenheiten (z.B. Carpooling) enthalten.<br/>
                    <br/>
                    Die ICL-Mobile App wird als Open-Source- und Open-Data-Lösung entwickelt und soll nicht nur für den Innovation Campus Lemgo, sondern auch für andere Standorte nutzbar sein. Das Projekt wird vom Bundesministerium für Digitales und Verkehr (BMDV) gefördert und läuft vom 01.01.2024 bis zum 30.06.2025.<br/>
                    <br/>
                    Es wurde von einem interdisziplinären Team aus Wissenschaftler:innen, IT-Entwickler:innen und Expert:innen der Mobilitätsbranche umgesetzt.<br/>
                    <br/>
                    <a href="#" @click="openLink('https://mein-lemgo.news/startschuss-fuer-nachhaltige-mobilitaet-iclmobil')">Ganzen Artikel hier lesen...</a><br/>
                    <br/>
                </div>

                <hr/>

                <div class="about-text">
                    Zur Umsetzung dieser App wurden die nachfolgenden Open-Source Frameworks und Open-Source Plugins verwendet:
                </div>

                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th class="label-cell">Framework</th>
                                <th class="text-cell">Link</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="label-cell">Framework7</td>
                                <td><a href="#" @click="openLink('https://framework7.io')">framework7</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Vue.js</td>
                                <td><a href="#" @click="openLink('https://vuejs.org')">Vue.js</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Cordova</td>
                                <td><a href="#" @click="openLink('https://cordova.apache.org')">Apache Cordova</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="data-table" style="padding-top: 20px">
                    <table>
                        <thead>
                            <tr>
                                <th class="label-cell">Plugin</th>
                                <th class="text-cell">Link</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="label-cell">Camera</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-camera')">plugin-camera</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">File</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-file')">plugin-file</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">File Transfer</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-file-transfer')">plugin-file-transfer</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">InAppBrowser</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-inappbrowser')">plugin-inappbrowser</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Fingerprint</td>
                                <td><a href="#" @click="openLink('https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio')">plugin-fingerprint</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Push</td>
                                <td><a href="#" @click="openLink('https://github.com/havesource/cordova-plugin-push')">plugin-push</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Diagnostic</td>
                                <td><a href="#" @click="openLink('https://github.com/dpa99c/cordova-diagnostic-plugin')">diagnostic-plugin</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Device</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-device')">plugin-device</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Vibration</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-vibration')">plugin-vibration</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Haptic Feedback</td>
                                <td><a href="#" @click="openLink('https://github.com/wrobins/cordova-plugin-haptic')">plugin-haptic</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Geolocation</td>
                                <td><a href="#" @click="openLink('https://github.com/apache/cordova-plugin-geolocation')">plugin-geolocation</a></td>
                            </tr>
                            <tr>
                                <td class="label-cell">Android Keyboard</td>
                                <td><a href="#" @click="openLink('https://github.com/SinGlEBW/cordova-plugin-android-keyboard')">plugin-android-keyboard</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <hr/>

                <f7-list dividers-ios >
                    <f7-list-item title="Turn on developer mode">
                        <template #footer>
                            {{ devMode ? 'Development Environment' : 'Production Environment' }}
                        </template>
                        <template #after>
                            <f7-toggle v-model:checked="devMode" />
                        </template>
                    </f7-list-item>
                </f7-list>

                <div class="about-footer text-align-center">
                    Made with lots of <i class="material-icons about-icon-large">favorite</i>by tiny robots<br />
                    <a href="#" @click="openLink('https://www.iosb-ina.fraunhofer.de/de/geschaeftsbereiche/assistenzsysteme.html')">@fraunhoferIOSB-INA</a> in Lemgo
                </div>
            </f7-block>

            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>

    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link, f7Card, f7CardHeader, f7CardContent, f7CardFooter } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import userService from '@/services/userService';

  import Logo from '../components/logo.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Link,
        f7Card,
        f7CardHeader,
        f7CardContent,
        f7CardFooter,
        NavBar,
        ToolBar,
        Logo
    },
    data() {
        return {
            title: this.$t('about.title'),
            appVersion: __APP_VERSION__
     };
    },
    computed: {
        inAppBrowser() {
            return this.$store.getters.getPluginInAppBrowser;
        },
        devMode: {
            get() {
                return this.$store.getters.getDevMode;
            },
            async set(v) {
                this.sendHapticFeedback("TOGGLE_ON", "SelectionChanged");
                this.$store.dispatch('setDevMode', { devmode: v });
                await this.$store.dispatch('setAppSettings');
                await this.logout();
            }
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    mounted() {
        f7ready(async () => {
        })
    },
    methods: {
        openLink(link) {
            if (this.inAppBrowser) {
                if (f7.device.cordova) {
                    this.inAppBrowser.open(link, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                }
            }
        },
        async logout() {
            let response = await userService.logout();
            if (response.status === 200) {
                this.sendHapticFeedback("CONFIRM", "Success");
                this.$store.dispatch('resetUserData');
                f7.view.current.router.navigate('/login', { history: false, clearPreviousHistory: true, ignoreCache: true });
                this.emitter.emit('close-verify-toast');
            } else {
                this.sendHapticFeedback("REJECT", "Error");
                f7.dialog.alert(this.$t('app.dialog.error.servertext'), this.$t('app.dialog.error.title'));
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
    hr {
        background: rgb(200, 200, 200);
        height: 1px;
        border: 0px;
        width: 60vw;
    }
    .about-header {
        color: rgba(100, 150, 150, 1);
        font-size: 22px;
        padding: 20px;
    }
    .about-text {
        color: rgba(100, 150, 150, 1);
        padding: 10px;
    }
    .about-footer {
        color: rgba(100, 150, 150, 1);
        font-size: 11px;
        padding: 20px;
    }
    .about-ride-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin-bottom: 10px;
        margin-top: 10px;
    }
    .about-ride-time,
    .about-ride-start,
    .about-ride-finish {
        font-weight: 500;
        margin-bottom: 10px;
    }
    .about-icon {
        font-size: 22px;
        color: gray;
        vertical-align: top;
        padding-right: 5px;
    }
    .about-icon-large {
        font-size: 28px;
        background: linear-gradient(to right, red, rgb(150, 0, 0));
        background-clip: text;
        color: transparent;
        vertical-align: middle;
        padding-right: 5px;
        display: inline-block;
    }
    .button-wrapper {
        padding-bottom: 30px;
    }
</style>