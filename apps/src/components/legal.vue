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
    <f7-block>
        <div v-html="content"></div>
    </f7-block>
</template>

<script>
  import { f7, f7ready, f7Block } from 'framework7-vue';

  import preferencesService from '../services/preferencesService';
  
  export default {
    props: {
        document: {
            type: String,
            default: 'imprint'
        }
    },
    components: {
        f7,
        f7ready,
        f7Block
    },
    data() {
        return {
            content: ''
        };
    },
    computed: {
        inAppBrowser() {
            return this.$store.getters.getPluginInAppBrowser;
        },
        specialPages: {
            get() {
                return this.$store.getters.getSpecialPages;
            },
            set(v) {
                this.$store.dispatch('setSpecialPages', v);
            }
        }
    },
    mounted() {
        f7ready(async () => {
            await this.getSpecialPages();
            this.showDocument();
        })
    },
    methods: {
        showDocument() {
            switch(this.document) {
                case 'dataprotection':
                    this.prepareText("dataprotection");
                    break;
                case 'terms':
                    this.prepareText("gtc");
                    break;
                case 'imprint':
                    this.prepareText("imprint");
                    break;
                default:
                    this.prepareText("imprint");
                    break;
            }
        },
        async getSpecialPages() {
            const response = await preferencesService.getSpecialPages();
            if (response.status === 200) {
                this.specialPages = response.data;
            }
        },
        prepareText(entryName) {
            if (!this.specialPages.by_language) { return; }

            let pages = this.specialPages.by_language[this.$i18n.locale];
            pages.forEach(page => {
                if (page.entry_name == entryName) {
                    this.content = page.content;
                }
            });
        },
        openLink(link) {
            if (this.inAppBrowser) {
                if (f7.device.cordova) {
                    this.inAppBrowser.open(link, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                }
            }
        }
    },
  };
</script>