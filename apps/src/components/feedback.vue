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
              style="min-height: 90vh" 
              swipe-to-close
              push
              backdrop
              :close-by-backdrop-click="true" 
              :close-by-outside-click="true" 
              class="feedback">
        <template #fixed>
            <div class="swipe-handler"></div>
        </template>

        <div class="feedback-top"></div>

        <f7-page-content>
            <f7-block>
                <div class="feedback-header text-align-center block-title block-title-small">
                    <i class="material-icons ride-icon-large">favorite</i><br /><br />
                    <div v-html="this.$t('app.sheet.feedback.header')"></div>
                </div>
                <div class="feedback-text text-align-center">
                    <div v-html="this.$t('app.sheet.feedback.text')"></div>
                </div>
                <form @submit.prevent @reset.prevent>
                    <f7-list strong-ios dividers-ios inset>
                        <f7-list-item v-if="Object.keys(localRide).length !== 0" accordion-item :title="this.$t('app.sheet.feedback.form.ride-data')">
                            <f7-accordion-content>
                                <f7-block>
                                    <div class="feedback-ride-wrapper">
                                        <div class="feedback-ride-time">
                                            <i class="material-icons ride-icon">schedule</i>{{ localRide.rideDate }} - {{ localRide.rideTime }}
                                        </div>
                                        <div class="feedback-ride-start">
                                            <i class="material-icons ride-icon">location_on</i>{{ localRide.rideStart }}
                                        </div>
                                        <div class="feedback-ride-finish">
                                            <i class="material-icons ride-icon">flag</i>{{ localRide.rideDestination }}
                                        </div>
                                    </div>
                                </f7-block>
                            </f7-accordion-content>
                        </f7-list-item>
                        <f7-list-input 
                            :label="this.$t('app.sheet.feedback.form.name-label')" 
                            :value="name"
                            v-model:value="name" 
                            :disabled="true"
                        ></f7-list-input>
                        <f7-list-input 
                            :label="this.$t('app.sheet.feedback.form.email-label')" 
                            :value="email"
                            v-model:value="email" 
                            :disabled="true"
                        ></f7-list-input>
                        <f7-list-input 
                            :label="this.$t('app.sheet.feedback.form.feedback-text-label')" 
                            type="textarea"
                            :maxlength="maxlength"
                            :placeholder="this.$t('app.sheet.feedback.form.feedback-text-placeholder')"
                            :error-message="this.$t('app.sheet.feedback.form.feedback-text-error')"
                            :error-message-force="v$.feedbackText.$error"
                            :value="feedbackText"
                            @input="feedbackText = $event.target.value;"
                            @blur="v$.feedbackText.$touch"
                            v-model:value="feedbackText"
                            data-cy="feedback-text-fld"
                        ></f7-list-input>
                        <div class="feedback-text-counter">{{ this.$t('app.sheet.feedback.form.remaining-chars') }} {{ remainingChars }}</div>
                    </f7-list>

                    <div class="feedback-voting-wrapper">
                        <div class="feedback-voting-text">
                            {{ this.$t('app.sheet.feedback.form.vote') }}
                        </div>
                        <f7-segmented round tag="p">
                            <f7-button round :active="thumbsUp" large @click="voting(0)" data-cy="feedback-thumbsup-btn"><i class="icon f7-icons" style="font-size: 22px">hand_thumbsup_fill</i></f7-button>
                            <f7-button round :active="thumbsDown" large @click="voting(1)" data-cy="feedback-thumbsdown-btn"><i class="icon f7-icons" style="font-size: 22px">hand_thumbsdown_fill</i></f7-button>
                        </f7-segmented>
                    </div>

                    <div class="button-wrapper">
                        <f7-button large fill @click="sendFeedback" data-cy="feedback-send-btn" style="--f7-button-large-text-transform: none">
                            {{ this.$t('app.sheet.feedback.button.send-feedback') }}
                        </f7-button>
                    </div>
                </form>
            </f7-block>
        </f7-page-content>
    </f7-sheet>
</template>

<script>
    import { f7, f7ready, f7Page, f7Block, f7Link, theme } from 'framework7-vue';

    import useVuelidate from '@vuelidate/core'
    import { required } from '@vuelidate/validators';

    import userService from '../services/userService';
  
    export default {
        components: {
            f7,
            f7ready,
            f7Page,
            f7Block,
            f7Link
        },
        data() {
            return {
                title: this.$t('app.sheet.feedback.title'),
                feedbackText: '',
                email: this.$store.getters.getUserEmail,
                name: this.$store.getters.getUserName,
                localRide: {},
                maxlength: 250,
                thumbsUp: false,
                thumbsDown: false,
                vote: 'neutral'
            };
        },
        setup() {
            return { v$: useVuelidate({ $scope: false }) }
        },
        validations() {
            return {
                feedbackText: {
                    required
                }
            }
        },
        computed: {
            remainingChars() {
                return this.maxlength - this.feedbackText.length;
            },
            hapticFeedback() {
                return this.$store.getters.getPluginHaptic;
            }
        },
        mounted() {
            f7ready(() => {
                this.emitter.on('set-ride-feedback-data', (ride) => {
                    this.localRide = ride;
                });
                this.emitter.on('open-feedback', () => {
                    this.sendHapticFeedback("CONTEXT_CLICK", "ImpactMedium");
                    f7.sheet.open('.feedback');
                });
            })
        },
        methods: {
            init() {
                console.log("SHEET FEEDBACK OPENED");
            },
            onClose() {
                console.log("SHEET CLOSING")
                this.feedbackText = '';
                this.localRide = {};
                this.thumbsDown = false;
                this.thumbsUp = false;
                this.vote = 'neutral';
                this.v$.$reset();
            },
            voting(vote) {
                try {
                    switch(vote) {
                        case 0:
                            this.thumbsUp = true;
                            this.thumbsDown = false;
                            this.vote = 'up'
                            this.sendHapticFeedback("SEGMENT_TICK", "SelectionChanged");
                            break;
                        case 1:
                            this.thumbsUp = false;
                            this.thumbsDown = true;
                            this.vote = 'down'
                            this.sendHapticFeedback("SEGMENT_TICK", "SelectionChanged");
                            break;
                        default:
                            break;
                    }
                } catch (err) {
                    console.log("ERROR: ", err)
                }
            },
            async sendFeedback() {
                try {
                    this.v$.$touch();
                    if (this.v$.$invalid)
                        return;
                    
                    const data = {
                        name: this.name,
                        email: this.email,
                        feedbackText: this.feedbackText,
                        rideData: this.localRide,
                        vote: this.vote
                    }
                    const response = await userService.feedback(data);
                    if (response.status === 200) {
                        this.sendHapticFeedback('CONFIRM', 'Success');
                        if (this.vote == 'neutral') {
                            this.emitter.emit('show-confetti', { emojis: false, poop: false });
                        } else if(this.vote == 'up') { 
                            this.emitter.emit('show-confetti', { emojis: true, poop: false });
                        } else {
                            this.emitter.emit('show-confetti', { emojis: true, poop: true });
                        }
                        f7.toast.show({
                            text: this.$t('app.sheet.feedback.form.feedback-sent'),
                            icon: theme.ios
                                ? '<i class="f7-icons">checkmark_alt_circle</i>'
                                : '<i class="material-icons">check_circle</i>',
                            position: 'center',
                            closeTimeout: 2000,
                            destroyOnClose: true
                        });
                    } else {
                        this.sendHapticFeedback('REJECT', 'Error');
                        f7.dialog.alert(this.$t('app.dialog.error.text'), this.$t('app.dialog.error.title'));
                    }
                    this.closeSheet();
                } catch(err) {
                    console.log("ERROR: ", err)
                }
            },
            closeSheet() {
                this.sendHapticFeedback('CONFIRM', 'ImpactSoft');
                f7.sheet.close('.feedback');
            },
            sendHapticFeedback(androidType, iosType) {
                if (this.hapticFeedback) {
                    this.hapticFeedback.sendHapticFeedback(androidType, iosType, function(error) {
                        console.error("HAPTIC ERROR: ", error);
                    });
                }
            }
        }
    };
</script>

<style scoped>
    .feedback-top {
        width: 100vw;
        height: 60px;
        background: linear-gradient(to bottom, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 0) 100%);
        position: absolute;
        top: 0;
        left: 0;
        z-index: 2;
    }
    .feedback-header {
        color: rgba(100, 150, 150, 1);
    }
    .feedback-text {
        color: rgba(100, 150, 150, 1);
    }
    .feedback-text-counter {
        padding-top: 10px;
        padding-left: 14px;
        font-size: 11px;
        color: gray;
    }
    .feedback-voting-text {
        font-size: 11px;
        color: gray;
    }
    .feedback-voting-wrapper {
        margin-bottom: 20px;
        margin-left: 30px;
        margin-right: 25px;
    }
    .feedback-ride-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin-bottom: 10px;
        margin-top: 10px;
    }
    .feedback-ride-time,
    .feedback-ride-start,
    .feedback-ride-finish {
        font-weight: 500;
        margin-bottom: 10px;
    }
    .ride-icon {
        font-size: 22px;
        color: gray;
        vertical-align: top;
        padding-right: 5px;
    }
    .ride-icon-large {
        font-size: 32px;
        background: linear-gradient(to right, red, rgb(150, 0, 0));
        background-clip: text;
        color: transparent;
        vertical-align: top;
        padding-right: 5px;
        display: inline-block;
    }
    .button-wrapper {
        padding-bottom: 30px;
    }
</style>