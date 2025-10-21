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

        <div class="wallet-background"></div>
        <f7-page :page-content="true" 
                 style="background-color: transparent !important" 
                 ptr 
                 :ptr-mousewheel="true"
                 @ptr:refresh="onRefresh"
        >

            <Logo ref="logo"/>

            <f7-block>
                <div class="grid grid-cols-3 grid-gap">
                    <div>
                        <f7-button style="height: 80px; --f7-button-border-radius: 12px; --f7-button-text-transform: none" fill>
                            <div class="icon_text_button">
                                <span class="wallet-text-bold">{{ totalRides }}</span>
                                <span class="wallet-text-normal">{{ this.$t('wallet.button.rides') }}</span>
                            </div>
                        </f7-button>
                    </div>
                    <div>
                        <f7-button style="height: 80px; --f7-button-border-radius: 12px; --f7-button-text-transform: none" fill>
                            <div class="icon_text_button">
                                <span class="wallet-text-bold">{{ totalDistance }} km</span>
                                <span class="wallet-text-normal">{{ this.$t('wallet.button.distance') }}</span>
                            </div>
                        </f7-button>
                    </div>
                    <div>
                        <f7-button style="height: 80px; --f7-button-border-radius: 12px; --f7-button-text-transform: none" fill>
                            <div class="icon_text_button">
                                <span class="wallet-text-bold">{{ totalDuration }} {{ this.$t('wallet.button.durationextension') }}</span>
                                <span class="wallet-text-normal">{{ this.$t('wallet.button.duration') }}</span>
                            </div>
                        </f7-button>
                    </div>
                </div>
                <div class="grid grid-cols-1">
                    <div>&nbsp;</div>
                </div>
                <div class="grid grid-cols-1">
                    <div>
                        <f7-button large fill style="--f7-button-border-radius: 12px; --f7-button-large-text-transform: none">
                            <div v-html="this.$t('wallet.button.co2saving')"></div>
                            &nbsp;
                            &nbsp;
                            <f7-icon color="white" icon="fa-solid fa-leaf" size="28"></f7-icon>
                            &nbsp;
                            ~ {{ totalEmmisions }} kg
                        </f7-button>
                    </div>
                </div>
            </f7-block>

            <hr style="width: 90vw; color: #96D35F;"/>

            <!-- <f7-block>
                <f7-button large fill style="height: 210px; --f7-button-border-radius: 12px; --f7-button-large-text-transform: none">
                    <div class="wallet-container">
                        <div class="wallet-main-icon-container">
                            <f7-icon color="white" ios="f7:checkmark_seal_fill" md="material:verified" size="64"></f7-icon>
                        </div>

                        <div class="wallet-main-content">
                            <div class="wallet-header-bold">
                                <div>{{ this.$t('wallet.score.scoretitle') }}</div>
                            </div>

                            <div class="wallet-score">
                                <div>{{ experienceScore }}/5</div>
                                <div class="wallet-score-icons">
                                    <f7-icon
                                        v-for="n in experienceScore" 
                                        :key="n" 
                                        color="white" 
                                        icon="fa-solid fa-leaf" 
                                        size="30">
                                    </f7-icon>
                                </div>
                            </div>

                            <div class="wallet-stats">
                                <div class="wallet-stat-item points">
                                    <div>{{ this.$t('wallet.score.points') }}</div>
                                    <div class="wallet-stat-points">{{ experiencePoints }}</div>
                                </div>
                                <div class="wallet-stat-item ranking">
                                    <div>{{ this.$t('wallet.score.ranking') }}</div>
                                    <div class="wallet-stat-points">{{ experienceLevel }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </f7-button>
            </f7-block> -->

            <f7-block>
                <div class="wallet-experience-wrapper">
                    <div class="wallet-container">
                        <div class="wallet-main-icon-container">
                            <f7-icon color="white" ios="f7:checkmark_seal_fill" md="material:verified" size="64"></f7-icon>
                        </div>

                        <div class="wallet-main-content">
                            <div class="wallet-header-bold">
                                <div>{{ this.$t('wallet.score.scoretitle') }}</div>
                            </div>

                            <div class="wallet-score">
                                <div>{{ experienceScore }}/5</div>
                                <div class="wallet-score-icons">
                                    <f7-icon
                                        v-for="n in experienceScore" 
                                        :key="n" 
                                        color="white" 
                                        icon="fa-solid fa-leaf" 
                                        size="30">
                                    </f7-icon>
                                </div>
                            </div>

                            <div class="wallet-stats">
                                <div class="wallet-stat-item points">
                                    <div>{{ this.$t('wallet.score.points') }}</div>
                                    <div class="wallet-stat-points">{{ experiencePoints }}</div>
                                </div>
                                <div class="wallet-stat-item ranking">
                                    <div>{{ this.$t('wallet.score.ranking') }}</div>
                                    <div class="wallet-stat-points">{{ experienceLevel }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </f7-block>

            <f7-block>
                <div class="wallet-statistics-wrapper">
                    <div class="wallet-container">
                        <div class="wallet-main-icon-container">
                            <f7-icon color="white" ios="f7:chart_bar_circle" md="material:leaderboard" size="64"></f7-icon>
                        </div>
                        <div class="wallet-header-bold">
                            <div>{{ this.$t('wallet.statistic.usagetitle') }}</div>
                        </div>
                        <canvas ref="chartContainer" class="wallet-chart-container"></canvas>
                        <div ref="iconContainer" class="wallet-stat-icon-container"></div>
                    </div>
                </div>
            </f7-block>

            <f7-block>
                <div class="wallet-highscores-wrapper">
                    <div class="wallet-container">
                        <div class="wallet-main-icon-container">
                            <f7-icon color="white" ios="f7:star_circle" md="material:stars" size="64"></f7-icon>
                        </div>
                        <div class="wallet-header-bold">
                            <div>{{ this.$t('wallet.ranking.top5title') }}</div>
                        </div>
                        
                        <div class="wallet-main-content scrollable-content">
                            <div class="data-table">
                                <table>
                                    <tbody>
                                        <tr v-for="user in limitedRanking" :key="user.id" class="ranking-item">
                                            <td class="wallet-icon-cell">
                                                <div class="wallet-rank">
                                                    {{ this.$t('wallet.ranking.rank') }}{{ user.id + 1 }}
                                                </div>
                                                <div class="wallet-icon">
                                                    <i class="material-icons" style="font-size: 34px;">emoji_events</i>
                                                </div>
                                            </td>
                                            <td class="label-cell">{{ user.name }}</td>
                                            <td class="numeric-cell">{{  user.points }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </f7-block>
            <div class="page-padding"></div>
        </f7-page>

        <ToolBar ref="toolBar" tabActive="none"/>

    </f7-page>
</template>

<script>
  import { f7, f7ready, f7Page, f7Block, f7Link } from 'framework7-vue';

  import { Bar } from 'vue-chartjs';
  import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
  import ChartDataLabels from 'chartjs-plugin-datalabels';
  ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ChartDataLabels);

  import NavBar from '../components/navbar.vue';
  import ToolBar from '../components/toolbar.vue';

  import userService from '../services/userService';
  import { customRound } from '../js/utilities/utils';

  import Logo from '../components/logo.vue';
  
  export default {
    components: {
        f7,
        f7ready,
        f7Page,
        f7Block,
        f7Link,
        NavBar,
        ToolBar,
        Bar,
        Logo
    },
    data() {
        return {
            title: this.$t('wallet.title'),
            maxRanking: 100
        };
    },
    computed: {
        totalRides() {
            return this.$store.getters.getTotalRides;
        },
        totalDistance() {
            return this.$store.getters.getTotalDistance;
        },
        totalDuration() {
            return this.$store.getters.getTotalDuration;
        },
        totalEmmisions() {
            return this.$store.getters.getTotalEmmisions;
        },
        experienceScore() {
            return Math.floor(this.$store.getters.getExperienceScore);
        },
        experiencePoints() {
            return this.$store.getters.getExperiencePoints;
        },
        experienceLevel() {
            return this.$store.getters.getExperienceLevel;
        },
        statistics() {
            return this.$store.getters.getStatistics;
        },
        ranking() {
            return this.$store.getters.getRanking;
        },
        limitedRanking() {
            return this.ranking.slice(0, this.maxRanking);
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
        f7ready(async () => {
            await this.getUserStatistics();
            this.createChart();
        })
    },
    methods: {
        onRefresh: async function (done) {
            await this.getUserStatistics();
            done();
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
                done();
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

            let statistics = [customRound(data.booking_percentage_per_mode.scooter) + customRound(data.booking_percentage_per_mode.bike),
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
        },
        createChart() {
            const icons = [
                { name: 'bike_scooter', size: '40' },
                { name: 'directions_car', size: '40' },
                { name: 'directions_bus', size: '40' },
                { name: 'directions_walk', size: '40' }
            ];
            const chartData = {
                labels: ['Shared', 'Bus', 'Car', 'Walk'],
                datasets: [{
                    label: 'Usage Statistics',
                    backgroundColor: '#fff',
                    data: this.statistics,
                    barPercentage: 1,
                    borderRadius: 4,
                    backgroundColor: (context) => {
                        const chart = context.chart;
                        const { ctx, chartArea } = chart;

                        if (!chartArea) {
                            return;
                        }
                        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
                        gradient.addColorStop(1, 'rgba(223, 238, 212, 1)');
                        return gradient;
                    }
                }]
            };

            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 200,
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        }
                    },
                    x: {
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false
                        },
                        border: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (tooltipItem) => `${tooltipItem.raw}%`
                        }
                    },
                    datalabels: {
                        display: false
                    }
                }
            };

            const myChart = new ChartJS(this.$refs.chartContainer, {
                type: 'bar',
                data: chartData,
                options: chartOptions,
                plugins: [{
                    afterRender: (chart) => {
                        const iconContainer = this.$refs.iconContainer;
                        iconContainer.innerHTML = '';

                        const meta = chart.getDatasetMeta(0);
                        meta.data.forEach((bar, index) => {
                            const barX = bar.x;

                            const iconElement = document.createElement('i');
                            iconElement.className = 'material-icons';
                            iconElement.textContent = icons[index].name;
                            iconElement.style.fontSize = `${icons[index].size}px`;
                            iconElement.style.position = 'absolute';
                            iconElement.style.left = `${barX - 20}px`;
                            iconElement.style.bottom = '15px';

                            const percentElement = document.createElement('div');
                            percentElement.textContent = `${chartData.datasets[0].data[index]}%`;
                            percentElement.style.position = 'absolute';
                            percentElement.style.left = `${barX - 13}px`;
                            percentElement.style.bottom = '-20px';
                            percentElement.style.color = '#fff';
                            percentElement.style.fontSize = '16px';
                            percentElement.style.fontWeight = 'bold';

                            iconContainer.appendChild(iconElement);
                            iconContainer.appendChild(percentElement);
                        });
                    }
                }]
            });
        },
        getRankIcons(rank) {
            switch (rank) {
                case 1:
                    return `
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>`;
                case 2:
                    return `
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_lefthalf_fill</i>`;
                case 3:
                    return `
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star</i>`;
                case 4:
                    return `
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_lefthalf_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star</i>`;
                case 5:
                    return `
                        <i class="icon f7-icons color-white" style="font-size:18px;">star_fill</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star</i>
                        <i class="icon f7-icons color-white" style="font-size:18px;">star</i>`;
                default:
                    return '';
            }
        }
    },
  };
</script>
<style scoped>
    .scrollable-content {
        height: 240px;
        margin-top: 50px;
        margin-bottom: 15px;
        margin-left: 15px;
        margin-right: 15px;
        overflow-y: auto; 
        overflow-x: hidden;
    }
</style>