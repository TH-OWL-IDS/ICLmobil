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
      
      <NavBar ref="navBar" 
              @search="updateSearchQuery"
              :title="title" 
              :large="true" 
              :showSearch="true" 
              :showIcons="false" 
              :navBack="true"/>

        <f7-page ref="pageContent"
                 :page-content="true">
            <div class="default-search-container">
                <div v-for="(group, index) in groupedItems" :key="index">
                    <f7-block-title large>{{ group.category }}</f7-block-title>
                    <f7-block-header>{{ group.description }}</f7-block-header>
                    <div ref="accordionList" class="list list-dividers-ios accordion-list media-list">
                        <ul>
                            <li v-for="item in group.items" 
                                :key="item.id" 
                                :id="`help-item-${item.id}`"
                                class="accordion-item" 
                                @click="sendHapticFeedback('CONTEXT_CLICK', 'ImpactLight')"
                            >
                                <a class="item-link item-content">
                                    <div class="item-inner">
                                        <div class="item-title-row">
                                            <div class="item-title">{{ item.title }}</div>
                                        </div>
                                        <div class="item-text">{{ item.text }}</div>
                                    </div>
                                </a>
                                <div class="accordion-item-content">
                                    <div class="block">
                                        <div v-html="item.content"></div>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>

    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import preferencesService from '../services/preferencesService';
  
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
            title: this.$t('help.title'),
            searchQuery: ''
     };
    },
    computed: {
        inAppBrowser() {
            return this.$store.getters.getPluginInAppBrowser;
        },
        supportTexts: {
            get() {
                return this.$store.getters.getSupportTexts;
            },
            set(v) {
                this.$store.dispatch('setSupportTexts', v);
            }
        },
        groupedItems() {
            let groups = {};

            if (!this.supportTexts.by_language) { return; }

            let items = this.supportTexts.by_language[this.$i18n.locale];
            items.forEach(item => {
                if (!groups[item.category]) {
                    groups[item.category] = { category: item.category, description: item.description, items: [] };
                }
                groups[item.category].items.push(item);
            });

            return Object.values(groups).map(group => ({
                category: group.category,
                description: group.description,
                items: group.items.filter(item => {
                    const query = this.searchQuery.toLowerCase();
                    return item.title.toLowerCase().includes(query) || 
                           item.text.toLowerCase().includes(query) || 
                           item.content.toLowerCase().includes(query) ||
                           item.description.toLowerCase().includes(query);
                }).map((item, index) => ({
                    ...item,
                    id: `${index}`
                }))
            })).filter(group => group.items.length > 0);
        },
        hapticFeedback() {
            return this.$store.getters.getPluginHaptic;
        }
    },
    mounted() {
        f7ready(async () => {
            await this.getSupportTexts();
            
            this.$nextTick(() => {
                const routeQuery = f7.views.main.router.currentRoute.query;
                let anchor = routeQuery ? routeQuery.anchor : null;
                if (anchor) {
                    this.navigateToHelpItem(anchor);
                }
            });
        })
    },
    methods: {
        navigateToHelpItem(itemId) {
            const element = document.getElementById(`${itemId}`);
            if (element) {
                const navbarHeight = this.$refs.navBar ? this.$refs.navBar.$el.offsetHeight : 44;
                const searchbarElement = document.querySelector('.searchbar');
                const searchbarHeight = searchbarElement ? searchbarElement.offsetHeight : 44;
                const totalOffset = navbarHeight + searchbarHeight + 5;

                const elementRect = element.getBoundingClientRect();
                const scrollTop = (window.pageYOffset + Math.floor(elementRect.top)) - totalOffset;
                
                const pageContent = this.$refs.pageContent?.$el?.querySelector('.page-content');

                pageContent.scrollTo({
                    top: scrollTop,
                    behavior: 'smooth'
                })

                const accordionItem = element.closest('.accordion-item');
                if (accordionItem) {
                    f7.accordion.open(accordionItem);
                }
            }
        },
        async getSupportTexts() {
            const response = await preferencesService.getSupport();
            if (response.status === 200) {
                this.supportTexts = response.data;
            }
        },
        openLink(link) {
            if (this.inAppBrowser) {
                if (f7.device.cordova) {
                    this.inAppBrowser.open(link, '_blank', 'location=yes,toolbar=yes,toolbarcolor=#ffffff,toolbarposition=top');
                }
            }
        },
        updateSearchQuery(query) {
            this.searchQuery = query;
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