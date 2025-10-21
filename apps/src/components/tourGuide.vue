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
    <div className="dialog custom-dialog">
        <div class="dialog-background"></div>
        <div className="dialog-inner">
            <swiper-container @init="onSwiperInit" 
                              @slidechange="onSlideChange"
                              :pagination="true" 
                              :space-between="50" 
                              speed="500" 
                              :loop="false"
                              class="tour-slider">
                <swiper-slide v-for="(slide, index) in slides" 
                              :key="index" 
                              class="tour-slide"> 
                    <Vue3Lottie
                        ref="anim"
                        :loop="true"
                        :autoPlay="true"
                        :speed="1"
                        :animation-data="slide.image"
                    />
                    <div class="slide-content">
                        <h2><div v-html="slide.title"></div></h2>
                        <div v-html="slide.text"></div>
                    </div>
                </swiper-slide>
            </swiper-container>

            <div class="tour-button-container">
                <f7-button @click="closeTour" class="button-left">{{ this.$t('tours.buttons.dismiss') }}</f7-button>
                <f7-button @click="nextTour" class="button-right">{{ this.$t('tours.buttons.next') }}</f7-button>
            </div>
        </div>
    </div>
</template>
<script>
    import { f7, f7ready } from 'framework7-vue';
    import { Vue3Lottie } from 'vue3-lottie';

    import home_slide1 from '../tours/home/slide1.json';
    import home_slide2 from '../tours/home/slide2.json';
    import home_slide3 from '../tours/home/slide3.json';
    import home_slide4 from '../tours/home/slide4.json';

    import planning_slide1 from '../tours/planning/slide1.json';
    import planning_slide2 from '../tours/planning/slide2.json';

    export default {
        components: {
            Vue3Lottie,
        },
        data() {
            return {
                isOpened: false,
                lottieControllers: [],
                controllerIndex: 0,
                customDialog: null,
                slides: [],
                homeSlide1: home_slide1,
                homeSlide2: home_slide2,
                homeSlide3: home_slide3,
                homeSlide4: home_slide4,
                planningSlide1: planning_slide1,
                planningSlide2: planning_slide2
            }
        },
        mounted() {
            f7ready(async () => {
                this.emitter.on('show-home-tour', () => {
                    if (!this.tourHomeState) {
                        this.setupHomeSlides();
                        this.setupDialog();
                        this.tourHomeState = true;
                    }
                });
                this.emitter.on('show-planning-tour', () => {
                    if (!this.tourPlanningState) {
                        this.setupPlanningSlides();
                        this.setupDialog();
                        this.tourPlanningState = true;
                    }
                });
            })
        },
        computed: {
            tourHomeState: {
                get() {
                    return this.$store.getters.getTourHomeTaken;
                },
                set(v) {
                    this.$store.dispatch('setTourHomeTaken', v);
                }
            },
            tourPlanningState: {
                get() {
                    return this.$store.getters.getTourPlanningTaken;
                },
                set(v) {
                    this.$store.dispatch('setTourPlanningTaken', v);
                }
            },
        },
        methods: {
            setupHomeSlides() {
                try {
                    this.slides = [
                        {
                            image: home_slide1,
                            title: this.$t('tours.home.slide1.title'),
                            text: this.$t('tours.home.slide1.description'),
                        },
                        {
                            image: home_slide2,
                            title: this.$t('tours.home.slide2.title'),
                            text: this.$t('tours.home.slide2.description'),
                        },
                        {
                            image: home_slide3,
                            title: this.$t('tours.home.slide3.title'),
                            text: this.$t('tours.home.slide3.description'),
                        },
                        {
                            image: home_slide4,
                            title: this.$t('tours.home.slide4.title'),
                            text: this.$t('tours.home.slide4.description'),
                        }
                    ];
                } catch (error) {
                    console.error("Error loading slides: ", error);
                }
            },
            setupPlanningSlides() {
                try {
                    this.slides = [
                        {
                            image: planning_slide1,
                            title: this.$t('tours.planning.slide1.title'),
                            text: this.$t('tours.planning.slide1.description'),
                        },
                        {
                            image: planning_slide2,
                            title: this.$t('tours.planning.slide2.title'),
                            text: this.$t('tours.planning.slide2.description'),
                        }
                    ];
                } catch (error) {
                    console.error("Error loading slides: ", error);
                }
            },
            setupDialog() {
                this.customDialog = f7.dialog.create({
                    el: '.custom-dialog',
                    on: {
                        open: () => {
                            this.isOpened = true;
                        },
                        close: () => {
                            this.isOpened = false;
                        },
                    },
                });
                this.customDialog.open();
                this.tourSlide = f7.swiper.get('.tour-slider');
            },
            onSwiperInit(swiper) {
            },
            onSlideChange(swiper) {
            },
            closeTour() {
                this.customDialog.close();
            },
            nextTour() {
                this.tourSlide.slideNext();
            }
        }
    };
</script>
<style scoped>
.slide-content {
    text-align: center;
    margin-top: -10px;
    color: #333 !important;
}
.tour-slide {
    margin-bottom: 20px;
}
.tour-button-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
}
.custom-dialog {
    background: white;
    z-index: 21000 !important;
}
.dialog-background {
    background-image: url( '../assets/backgrounds/tour_bg.svg' );
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    height: 60%;
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1;
}
.button-left,
.button-right {
    flex: 1; /* Macht die Buttons gleichmäßig breit */
    margin: 0 5px; /* Optional: Abstand zwischen den Buttons */
}
</style>