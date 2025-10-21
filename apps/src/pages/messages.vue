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
    
    <NavBar ref="navBar" :title="title" :large="true" :showSearch="false" :showIcons="true" :navBack="true"/>

      <f7-page :page-content="true">

          <f7-block-title medium>{{ this.$t('account.page.messages.header') }}</f7-block-title>

          <div v-if="messages.length == 0" class="no-messages-background">
              <div class="no-messages-text text-align-center block-title block-title-medium">
                  {{ this.$t('account.page.messages.nomessages-found') }}
              </div>
          </div>
          <div v-else>
            <f7-list dividers-ios strong inset accordion-list>
                <f7-list-item 
                    swipeout
                    accordion-item 
                    v-for="(message, index) in messages" 
                    :key="message.id" 
                    :title="message.createdAt"
                    :swipeout="!accordionOpen[index]"
                    @swipeout:opened="onSwipeOpen(index)"
                    @swipeout:closed="onSwipeClose"
                    @accordion:beforeopen="onAccordionBeforeOpen"
                    @accordion:opened="onAccordionOpen(index)"
                    @accordion:closed="onAccordionClose(index)">
                    <template #media>
                      <i class="f7-icons">envelope_badge</i>
                    </template>
                  <f7-accordion-content>
                    <f7-block>
                      <p>
                        {{ message.content }}
                      </p>
                    </f7-block>
                  </f7-accordion-content>
                  <f7-swipeout-actions right>
                      <f7-swipeout-button overswipe delete @click="deleteMessage(message)">{{ this.$t('account.page.messages.swipeout.delete') }}</f7-swipeout-button>
                  </f7-swipeout-actions>
                </f7-list-item>
            </f7-list>
          </div>
          
          <div class="page-padding"></div>
      </f7-page>

      <ToolBar ref="toolBar" :tabActive="tabActive"/>

  </f7-page>
</template>

<script>
import { f7, f7ready, f7Page, f7Block, f7Link, f7List, f7ListItem, f7AccordionContent, theme } from 'framework7-vue';

import NavBar from '../components/navbar.vue';
import ToolBar from '../components/toolbar.vue';

import messageService from '../services/messageService';

export default {
  components: {
      f7,
      f7ready,
      f7Page,
      f7Block,
      f7Link,
      f7List,
      f7ListItem,
      f7AccordionContent,
      NavBar,
      ToolBar
  },
  data() {
    return {
      title: this.$t('account.page.messages.title'),
      tabActive: 4,
      accordionOpen: {},
      swipeoutOpened: null
    };
  },
  computed: {
    messages: {
      get() {
          return this.$store.getters.getMessages(this.$i18n.locale);
      }
    },
    messagesUnformated: {
      get() {
        return this.$store.getters.getMessagesUnformated;
      }
    },
    hapticFeedback() {
      return this.$store.getters.getPluginHaptic;
    }
  },
  methods: {
    onSwipeOpen(index) {
      this.swipeoutOpened = true;
    },
    onSwipeClose() {
      this.swipeoutOpened = null;
    },
    onAccordionBeforeOpen(prevent) {
      if (this.swipeoutOpened !== null) {
        prevent();
      }
    },
    onAccordionOpen(index) {
      this.accordionOpen[index] = true;
    },
    onAccordionClose(index) {
      this.accordionOpen[index] = false;
    },
    async deleteMessage(message) {
      try {
        const index = this.messages.indexOf(message);
        const unformatedIndex = this.messagesUnformated.findIndex(m => m.id === message.id);

        if (index !== -1) {
          let data = { message_id: message.id.toString() }
          let response = await messageService.deleteMessage(data);

          if (response.status === 200) {
            this.messages.splice(index, 1);
            this.messagesUnformated.splice(unformatedIndex, 1);

            this.sendHapticFeedback("CONFIRM", "Success");
            this.$store.dispatch('setMessages', { messages:  this.messagesUnformated });

            f7.toast.show({
              text: this.$t('account.page.messages.toast.title'),
              icon: theme.ios
                ? '<i class="f7-icons">checkmark_alt_circle</i>'
                : '<i class="material-icons">check_circle</i>',
              position: 'center',
              closeTimeout: 2000,
              destroyOnClose: true
            });
          } else {
            this.sendHapticFeedback("REJECT", "Error");

            f7.toast.show({
              text: this.$t('account.page.messages.toast.could-not-delete'),
              icon: theme.ios
                ? '<i class="f7-icons">exclamationmark_triangle</i>'
                : '<i class="material-icons">error</i>',
              position: 'center',
              closeTimeout: 2000,
              destroyOnClose: true
            });
          }
        }
      } catch(err) {
        console.log("ERROR: ", err)
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