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
            <Legal ref="dataprotection" document="dataprotection" />
            
            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>
    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import Logo from '../components/logo.vue';
  import Legal from '../components/legal.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Link,
        NavBar,
        ToolBar,
        Logo,
        Legal
    },
    data() {
        return {
            title: this.$t('preferences.page.dataprotection.title')
     };
    },
    mounted() {
        f7ready(async () => {
        })
    },
    methods: {
    },
  };
</script>