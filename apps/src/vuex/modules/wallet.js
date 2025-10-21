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

import { AppTestData } from "@/data/appTestData";

// Wallet Setup
export const wallet = {
    state: () => ({
        data: {
            total_rides: null,
            total_distance: null,
            total_duration: null,
            total_emmisions: null,
            experience_score: null,
            experience_points: null,
            experience_level: null,
            statistics: null,
            ranking: null,
        },
        default: {
            data: {
                total_rides: AppTestData.WALLET_DATA.total_rides,
                total_distance: AppTestData.WALLET_DATA.total_distance,
                total_duration: AppTestData.WALLET_DATA.total_duration,
                total_emmisions: AppTestData.WALLET_DATA.total_emmisions,
                experience_score: AppTestData.WALLET_DATA.experience_score,
                experience_points: AppTestData.WALLET_DATA.experience_points,
                experience_level: AppTestData.WALLET_DATA.experience_level,
                statistics: AppTestData.STATISTICS,
                ranking: AppTestData.RANKING,
            }
        }
    }),
    mutations: {
        RESET_WALLET_DATA: state => {
            Object.assign(state.data, state.default.data);
        },
        SET_TOTAL_RIDES(state, totalRides) {
            state.data.total_rides = totalRides;
        },
        SET_TOTAL_DISTANCE(state, totalDistance) {
            state.data.total_distance = totalDistance;
        },
        SET_TOTAL_DURATION(state, totalDuration) {
            state.data.total_duration = totalDuration;
        },
        SET_TOTAL_EMMISIONS(state, totalEmmisions) {
            state.data.total_emmisions = totalEmmisions;
        },
        SET_EXPERIENCE_SCORE(state, experienceScore) {
            state.data.experience_score = experienceScore;
        },
        SET_EXPERIENCE_POINTS(state, experiencePoints) {
            state.data.experience_points = experiencePoints;
        },
        SET_EXPERIENCE_LEVEL(state, experienceLevel) {
            state.data.experience_level = experienceLevel;
        },
        SET_STATISTICS(state, statistics) {
            state.data.statistics = statistics;
        },
        SET_RANKING(state, ranking) {
            state.data.ranking = ranking;
        }
    },
    actions: {
        resetWalletData: ({ commit }) => {
            commit('RESET_WALLET_DATA', '');
        },
        setTotalRides({ commit }, { totalRides }) {
            commit('SET_TOTAL_RIDES', totalRides);
        },
        setTotalDistance({ commit }, { totalDistance }) {
            commit('SET_TOTAL_DISTANCE', totalDistance);
        },
        setTotalDuration({ commit }, { totalDuration }) {
            commit('SET_TOTAL_DURATION', totalDuration);
        },
        setTotalEmmisions({ commit }, { totalEmmisions }) {
            commit('SET_TOTAL_EMMISIONS', totalEmmisions);
        },
        setExperienceScore({ commit }, { experienceScore }) {
            commit('SET_EXPERIENCE_SCORE', experienceScore);
        },
        setExperiencePoints({ commit }, { experiencePoints }) {
            commit('SET_EXPERIENCE_POINTS', experiencePoints);
        },
        setExperienceLevel({ commit }, { experienceLevel }) {
            commit('SET_EXPERIENCE_LEVEL', experienceLevel);
        },
        setStatistics({ commit }, { statistics }) {
            commit('SET_STATISTICS', statistics);
        },
        setRanking({ commit }, { ranking }) {
            commit('SET_RANKING', ranking);
        }
    },
    getters : {
        getTotalRides: state => state.data.total_rides,
        getTotalDistance: state => state.data.total_distance,
        getTotalDuration: state => state.data.total_duration,
        getTotalEmmisions: state => state.data.total_emmisions,
        getExperienceScore: state => state.data.experience_score,
        getExperiencePoints: state => state.data.experience_points,
        getExperienceLevel: state => state.data.experience_level,
        getStatistics: state => state.data.statistics,
        getRanking: state => state.data.ranking,
    }
}