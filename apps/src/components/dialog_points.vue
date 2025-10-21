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
  import { f7 } from 'framework7-vue';
  import $ from 'dom7';
  
  export default {
    components: {
        f7
    },
    data() {
        return {
            dialog: null,
            file: this.$store.getters.getPluginFile
        };
    },
    methods: {
        showDialog(points) {
            this.dialog = f7.dialog.create({
                title: points > 0 ? this.$t('app.dialog.points.title') : this.$t('app.dialog.points.title-negative'),
                text: this.getDialogHtml(points),
                buttons: [
                    {
                        text: this.$t('app.dialog.cancel'),
                    },
                    {
                        text: this.$t('app.dialog.share'),
                        onClick: async () => {
                            console.log("START SHARING DIALOG...");
                            this.shareContent(points);
                        }
                    }
                ],
                animate: true
            }).open();
            
            this.$nextTick(() => {
                setTimeout(() => {
                    const $dialogEl = $('.dialog .points-help');
                    if ($dialogEl.length) {
                        $dialogEl.on('click', (e) => {
                            e.preventDefault();
                            this.closeDialog();
                        });
                    }
                }, 100);
            });
        },
        getDialogHtml(points) {
            const textTop = points > 0 ? this.$t('app.dialog.points.text-top') : this.$t('app.dialog.points.text-top-negative');
            const textCenter = this.$t('app.dialog.points.text-center');
            const textBottom = this.$t('app.dialog.points.text-bottom');
            const stars = points > 0 ? `<div style="display: flex; justify-content: center; margin-bottom: 16px;">
                                            <i class="f7-icons" style="font-size: 25px !important">star_fill</i><i class="f7-icons" style="font-size: 25px !important;">star_fill</i><i class="f7-icons" style="font-size: 25px !important">star_fill</i>
                                        </div>` : '';
            return `${stars}
                    ${textTop}
                    <span style="font-size: 30px; font-weight: 900">${points}</span><br />
                    ${textCenter}
                    ${textBottom}
            `;
        },
        shareContent(points) {
            if (f7.device.cordova && 
                window.plugins && 
                window.plugins.socialsharing) {
                const text = points > 0 ? this.$t('app.dialog.points.text-share-left') : this.$t('app.dialog.points.text-share-left-negative');
                const message = text + points + this.$t('app.dialog.points.text-share-right') + this.$t('app.dialog.points.text-share-message');
                const subject = 'ICL-Mobile App';
                const url = 'https://www.icl-owl.de/icl-mobil';
                const file = 'https://icl-mobile-data.s3.eu-central-1.amazonaws.com/icons/icon-512x512.png';

                window.plugins.socialsharing.share(
                    message,
                    subject,
                    file,
                    url,
                    (result) => {
                        console.log("Teilen erfolgreich: " + result);
                        f7.views.current.router.refreshPage();
                    },
                    (err) => {
                        console.log("Teilen fehlgeschlagen: " + err);
                        f7.views.current.router.refreshPage();
                    }
                );
            } else {
                console.error("SocialSharing Plugin nicht verfügbar.");
            }
        },
        closeDialog() {
            if (this.dialog) {
                this.dialog.close();
                this.dialog = null;
            }
        }
    },
  };
</script>