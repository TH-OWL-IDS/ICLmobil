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
      
        <NavBar ref="navBar" :title="title" :large="true" :showSearch="false" :showIcons="true"/>
        
        <div class="fab fab-right-bottom fab-above-toolbar" v-if="showScrollTopFab">
            <a href="#" @click.prevent="scrollToTop">
                <i class="icon f7-icons">arrow_up</i>
            </a>
        </div>

        <f7-page ref="pageContent"
                 :page-content="true"
                 ptr 
                 :ptr-mousewheel="true"
                 @ptr:refresh="onRefresh"
        >
            <f7-block>
                <f7-button href="/planning" @click="sendHapticFeedback('CONFIRM', 'ImpactMedium')" large fill style="--f7-button-large-text-transform: none"><f7-icon ios="f7:map_pin_ellipse" md="material:explore"></f7-icon>&nbsp; {{ this.$t('home.button.plantrip') }}</f7-button>
            </f7-block>

            <f7-block>
                <f7-segmented round ref="segmentedControl">
                    <f7-button round outline large
                    :class="{ 'button-active': activeOption === 0 }"
                    @click="toggleFilter(0)">
                        <i class="material-icons news-icon">{{ iconFood }}</i>
                    </f7-button>
                    <f7-button round outline large
                    :class="{ 'button-active': activeOption === 1 }"
                    @click="toggleFilter(1)">
                        <i class="material-icons news-icon">{{ iconCampus }}</i>
                    </f7-button>
                    <f7-button round outline large
                    :class="{ 'button-active': activeOption === 2 }"
                    @click="toggleFilter(2)">
                        <i class="material-icons news-icon">{{ iconEvents }}</i>
                    </f7-button>
                    <f7-button round outline large
                    :class="{ 'button-active': activeOption === 3 }" 
                    @click="toggleFilter(3)">
                        <i class="material-icons news-icon">{{ iconICL }}</i>
                    </f7-button>
                </f7-segmented>
            </f7-block>

            <f7-block-title medium data-cy="news-category-title">{{ newsTitle }}</f7-block-title>
            <div v-if="Object.keys(filteredNews).length === 0">
                <div class="news-missing-wrapper">
                    <div class="news-background"></div>
                    <div class="news-missing-text text-align-center">
                        {{ $t('home.no-news') }}
                    </div>
                </div>
            </div>
            <div class="list inset list-strong media-list no-chevron" style="--f7-list-strong-bg-color: #96D35F">
                <ul>
                    <li v-for="news in filteredNews" :key="news.id">
                        <a href="#" @click="openSheet('.iclNewsSheet', news)" class="item-link">
                            <div class="item-content">
                                <div class="item-inner">
                                    <div class="item-title-row">
                                        <div v-html="news.header" class="item-title newsTitle"></div>
                                    </div>
                                    <div v-html="news.subHeaderCombined" class="item-subtitle newsSubtitle"></div>
                                    <div v-html="news.previewText" class="item-text newsText"></div>
                                </div>
                            </div>
                        </a>
                    </li>
                </ul>
                <div class="button-wrapper">
                    <f7-button v-if="activeOption === 0" href="#" @click="openLink(iclFoodURL)" fill large>{{ this.$t('home.button.get-more-food-news') }}</f7-button>
                    <f7-button v-else-if="activeOption === 1 || activeOption === 3" href="#" @click="openLink(iclNewsURL)" fill large>{{ this.$t('home.button.get-more-news') }}</f7-button>
                    <f7-button v-else-if="activeOption === 2" href="#" @click="openLink(iclEventsURL)" fill large>{{ this.$t('home.button.get-more-events') }}</f7-button>
                </div>
            </div>
            <div class="page-padding"></div>
        </f7-page>

        <f7-sheet @sheet:opened="init" 
                  @sheet:closed="onClose"
                  swipe-handler=".swipe-handler" 
                  style="height: 40vh" 
                  swipe-to-close 
                  push 
                  backdrop 
                  :close-by-backdrop-click="true" 
                  :close-by-outside-click="true" 
                  class="iclNewsSheet">
            <template #fixed>
                <div class="swipe-handler"></div>
            </template>
            <f7-page :page-content="true">
                <f7-block-title large><div v-html="iclNewsTitle"></div></f7-block-title>
                <f7-block-title medium><div v-html="iclNewsHeader"></div></f7-block-title>
                <f7-block-header>
                    <div v-html="iclNewsSubHeaderCombined"></div>
                </f7-block-header>
                <f7-block>
                    <img v-if="iclNewsImage" class="newsImage"
                        :src="iclNewsImage"
                    />
                    <div v-html="iclNewsText"></div>
                    <div v-if="iclNewsLink" class="button-wrapper">
                        <f7-button href="#"  @click="openLink(iclNewsLink)" fill large style="--f7-button-large-text-transform: none">{{ this.$t('home.button.readmore') }}</f7-button>
                    </div>
                </f7-block>
            </f7-page>
        </f7-sheet>

        <ToolBar ref="toolBar" :tabActive="tabActive"/>
    </f7-page>
</template>

<script>
  import { getDevice }  from 'framework7';
  import { f7, f7ready, f7Page, f7Block, f7Tabs, f7Tab, f7Link, f7Sheet } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import newsService from '../services/newsService';
  import messageService from '../services/messageService';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Tabs,
        f7Tab,
        f7Link,
        f7Sheet,
        NavBar,
        ToolBar
    },
    data() {
        return {
            device: getDevice(),
            title: this.$t('home.title'),
            tabActive: 1,
            iclNewsTitle: '',
            iclNewsHeader: '',
            iclNewsSubHeaderCombined: '',
            iclNewsSubHeader: '',
            iclNewsSubHeader2: '',
            iclNewsText: '',
            iclNewsLink: '',
            iclNewsImage: null,
            iclFoodURL: '',
            iclNewsURL: '',
            iclEventsURL: '',
            maxTextLength: 500,
            activeOption: 0,
            iconFood: 'restaurant',
            iconICL: 'bike_scooter',
            iconCampus: 'newspaper',
            iconEvents: 'calendar_month',
            newsTitle: '',
            showScrollTopFab: false
        };
    },
    computed: {
        pushToken() {
            return this.$store.getters.getPushToken;
        },
        faceIDLogin() {
            return this.$store.getters.getFaceIDLogin;
        },
        userName() {
            return this.$store.getters.getUserName;
        },
        news: {
            get() {
                return this.$store.getters.getNews;
            },
            set(v) {
                this.$store.dispatch('setNews', { news: v });
            }
        },
        iclNews: {
            get() {
                return this.$store.getters.getIclNews;
            },
            set(v) {
                this.$store.dispatch('setIclNews', { news: v });
            }
        },
        campusNews: {
            get() {
                return this.$store.getters.getCampusNews;
            },
            set(v) {
                this.$store.dispatch('setCampusNews', { news: v });
            }
        },
        foodNews: {
            get() {
                return this.$store.getters.getFoodNews;
            },
            set(v) {
                this.$store.dispatch('setFoodNews', { news: v });
            }
        },
        eventNews: {
            get() {
                return this.$store.getters.getEventNews;
            },
            set(v) {
                this.$store.dispatch('setEventNews', { news: v });
            }
        },
        filteredNews() {
            this.switchNewsTitle();
            if (this.activeOption === null) return;

            const types = ["food", "campus", "events", "icl"];
            const selectedType = types[this.activeOption];

            return this.news.filter(option => option.type === selectedType);
        },
        inAppBrowser() {
            return this.$store.getters.getPluginInAppBrowser;
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    created() {
        this.emitter.on('deviceReady', () => {
            // Check if faceID or fingerprint is available on device
            if (this.device.cordova) {
                Fingerprint.isAvailable(this.fingerprintIsAvailableSuccess,
                                        this.fingerprintIsAvailableError,
                                        null);
            }
        });
    },
    mounted() {
        f7ready(async () => {
            await this.getNews();
            this.emitter.emit('show-home-tour');
            this.$nextTick(() => {
                const pageContent = this.$refs.pageContent?.$el?.querySelector('.page-content');
                if (pageContent) {
                    pageContent.addEventListener('scroll', this.handleScroll);
                }
            });
        })
    },
    beforeDestroy() {
        const pageContent = this.$refs.pageContent?.$el?.querySelector('.page-content');
        if (pageContent) {
            pageContent.removeEventListener('scroll', this.handleScroll);
        }
    },
    methods: {
        init() {
            console.log("SHEET NEWS OPENED")
        },
        onClose() {
            console.log("SHEET CLOSING")
        },
        onRefresh: async function (done) {
            await this.getNews();
            done();
        },
        switchNewsTitle() {
            switch (this.activeOption) {
                case 0: {
                    this.newsTitle = this.$t('home.newstitle1');
                    break;
                }
                case 1: {
                    this.newsTitle = this.$t('home.newstitle2');
                    break;
                }
                case 2: {
                    this.newsTitle = this.$t('home.newstitle3');
                    break;
                }
                case 3: {
                    this.newsTitle = this.$t('home.newstitle4');
                    break;
                }
                default: {
                    this.newsTitle = this.$t('home.newstitle5');
                    break;
                }
            }
        },
        async getNews() {
            const response = await newsService.getNews();
            if (response.status === 200) {
                this.reparseNews(response.data, this.$i18n.locale);
            }
        },
        reparseNews(data, selectedLanguage) {
            var parsedNews = [];
            var parsedICLNews = [];
            var parsedCampusNews = [];
            var parsedEventNews = [];
            var parsedFoodNews = [];

            if (data.ICL_NEWS) {
                this.iclNewsURL = data.ICL_NEWS.more_link_url;
                var parsedICLNews = data.ICL_NEWS.entries.map(item => ({
                    id: item.id,
                    title: item.title[selectedLanguage],
                    image: item.image,
                    header: item.header[selectedLanguage],
                    subHeaderCombined: item.subHeader2[selectedLanguage] ? item.subHeader[selectedLanguage] + ' - ' + item.subHeader2[selectedLanguage] : item.subHeader[selectedLanguage],
                    subHeader: item.subHeader[selectedLanguage],
                    subHeader2: item.subHeader2[selectedLanguage],
                    previewText: item.previewText[selectedLanguage],
                    text: item.text[selectedLanguage],
                    sourceURL: item.source_url,
                    type: "icl"
                }));
            }

            if (data.CAMPUS_NEWS) {
                this.iclEventsURL = data.CAMPUS_NEWS.more_link_url;
                var parsedCampusNews = data.CAMPUS_NEWS.entries.map(item => ({
                    id: item.id,
                    title: item.title[selectedLanguage],
                    image: item.image,
                    header: item.header[selectedLanguage],
                    subHeaderCombined: item.subHeader2[selectedLanguage] ? item.subHeader[selectedLanguage] + ' - ' + item.subHeader2[selectedLanguage] : item.subHeader[selectedLanguage],
                    subHeader: item.subHeader[selectedLanguage],
                    subHeader2: item.subHeader2[selectedLanguage],
                    previewText: item.previewText[selectedLanguage],
                    text: item.text[selectedLanguage],
                    sourceURL: item.source_url,
                    type: "campus"
                }));
            }

            if (data.EVENTS) {
                this.iclEventsURL = data.EVENTS.more_link_url;
                var parsedEventNews = data.EVENTS.entries.map(item => ({
                    id: item.id,
                    title: item.title[selectedLanguage],
                    image: item.image,
                    header: item.header[selectedLanguage],
                    subHeaderCombined: item.subHeader2[selectedLanguage] ? item.subHeader[selectedLanguage] + ' - ' + item.subHeader2[selectedLanguage] : item.subHeader[selectedLanguage],
                    subHeader: item.subHeader[selectedLanguage],
                    subHeader2: item.subHeader2[selectedLanguage],
                    previewText: item.previewText[selectedLanguage],
                    text: item.text[selectedLanguage],
                    sourceURL: item.source_url,
                    type: "events"
                }));
            }

            if (data.FOOD_AND_DRINKS) {
                this.iclFoodURL = data.FOOD_AND_DRINKS.more_link_url;
                var parsedFoodNews = data.FOOD_AND_DRINKS.entries.map(item => ({
                    id: item.id,
                    title: item.title[selectedLanguage],
                    image: item.image,
                    header: item.header[selectedLanguage],
                    subHeaderCombined: item.subHeader2[selectedLanguage] ? item.subHeader[selectedLanguage] + ' - ' + item.subHeader2[selectedLanguage] : item.subHeader[selectedLanguage],
                    subHeader: item.subHeader[selectedLanguage],
                    subHeader2: item.subHeader2[selectedLanguage],
                    previewText: item.previewText[selectedLanguage],
                    text: item.text[selectedLanguage],
                    sourceURL: item.source_url,
                    type: "food"
                }));
            }

            parsedNews = [...parsedICLNews, ...parsedCampusNews, ...parsedEventNews, ...parsedFoodNews]

            this.news = parsedNews;
            this.iclNews = parsedICLNews;
            this.campusNews = parsedCampusNews;
            this.eventNews = parsedEventNews;
            this.foodNews = parsedFoodNews;
        },
        fingerprintIsAvailableSuccess(result) {
            // Check if user wants to authenticate using biometric features
            // and if we still have his credentials on file
            var that = this;
            if (this.faceIDLogin &&
                this.userName) {
                console.log("LOADING BIOMETRIC SECRETS");
                Fingerprint.loadBiometricSecret({
                    description: "User Token",
                    disableBackup: true, // always disabled on Android
                }, function(token) {
                    that.$store.dispatch('setUserToken', { token: token });
                    console.log("Token erfolgreich mit biometrischer Authentifizierung geladen", token);
                    that.registerPushToken();
                }, function(error) {
                    console.error("Fehler beim Laden des Tokens", error);
                });
            }
        },
        fingerprintIsAvailableError(error) {
            console.log("FINGERPRINT IS NOT AVAILABLE: ", error);
        },
        truncateText(text) {
            if (text.length > this.maxTextLength) {
                return text.slice(0, this.maxTextLength) + '...';
            }
            return text;
        },
        openSheet(sheet, news) {
            this.iclNewsTitle = news.title;
            this.iclNewsHeader = news.header;
            this.iclNewsSubHeaderCombined = news.subHeader2 ? news.subHeader + " - " + news.subHeader2 : news.subHeader;
            this.iclNewsSubHeader = news.subHeader;
            this.iclNewsSubHeader2 = news.subHeader2;
            this.iclNewsText = this.truncateText(news.text);
            this.iclNewsLink = news.sourceURL;
            this.iclNewsImage = news.image;
            this.sendHapticFeedback("CONTEXT_CLICK", "ImpactMedium");
            f7.sheet.open(sheet);
        },
        openLink(link) {
            console.log("LINK: ", link)
            if (this.inAppBrowser) {
                if (f7.device.cordova) {
                    this.sendHapticFeedback("CONTEXT_CLICK", "ImpactHeavy");
                    this.inAppBrowser.open(link, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                }
            }
        },
        async registerPushToken() {
            if (!this.device.cordova) return;           // Are we on device?
            if (!this.pushToken) return;                // Is there a push token yet?

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
        sendHapticFeedback(androidType, iosType) {
            if (this.hapticFeedback) {
                this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                    console.error("HAPTIC ERROR: ", error);
                });
            }
        },
        toggleFilter(option) {
            this.activeOption = option;
            this.updateHighlight();
            this.sendHapticFeedback("SEGMENT_TICK", "SelectionChanged");
        },
        updateHighlight() {
            const highlight = this.$refs.segmentedControl.$el.querySelector('.segmented-highlight');
            if (highlight) {
                highlight.style.display = this.activeOption === null ? 'none' : 'block';
            }
        },
        handleScroll(e) {
            const scrollTop = e.target.scrollTop;
            this.showScrollTopFab = scrollTop > 200;
        },
        scrollToTop() {
            const pageContent = this.$refs.pageContent?.$el?.querySelector('.page-content');
            if (pageContent) {
                pageContent.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
    },
  };
</script>
<style scoped>
    .newsImage {
        display: block;
        float: left;
        aspect-ratio: 1;
        object-fit: cover;
        border-radius: 10%;
        margin-right: 1rem;
        max-width: 8em;
        border-image: conic-gradient(#302c2900 0 0) fill 0;
    }
    .newsTitle {
        color: #fff;
    }
    .newsSubtitle {
        color: #49672e;
    }
    .newsText {
        color: #17210e;
    }
    .news-background {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        min-height: 40vh;
        width: 100%;
        z-index: 0;
    }
    .news-background::before {
        content: '';
        background-image: url('../assets/backgrounds/sad_bot.svg');
        background-repeat: no-repeat;
        background-position: center;
        background-size: auto;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0.2;
        filter: grayscale(100%);
        z-index: -1;
    }
    .news-missing-text {
        color: rgba(100, 150, 150, 1);
        font-size: larger;
        font-weight: 600;
    }
    .button-wrapper {
        padding: 20px 0px 0px 0px;
    }
    :deep(.block-title) {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    :deep(.block-title div) {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    .fab-above-toolbar {
        /* Always above the toolbar, with a little extra space */
        bottom: calc(var(--f7-toolbar-height, 44px) + var(--f7-safe-area-bottom, 0px) + 16px) !important;
        /* Make sure it's above the toolbar z-index */
        z-index: 9999;
    }
    .fab-above-toolbar > a {
        background: rgb(102, 144, 65) !important; /* Bright orange */
        color: #fff !important; /* White icon */
        box-shadow: 0 4px 16px rgba(0,0,0,0.18), 0 1.5px 4px rgba(0,0,0,0.12);
        border-radius: 50%;
        transition: background 0.2s;
    }
    .fab-above-toolbar > a:hover, .fab-above-toolbar > a:active {
        background: rgb(84, 118, 53) !important; /* Slightly darker on hover/active */
    }
</style>