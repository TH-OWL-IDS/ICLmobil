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

// Tours Setup
export const tours = {
    state: () => ({
        data: {
            tour_home_taken: false,
            tour_planning_taken: false
        },
        default: {
            data: {
                tour_home_taken: false,
                tour_planning_taken: false
            }
        }
    }),
    mutations: {
        RESET_TOUR_DATA: state => {
            Object.assign(state.data, state.default.data);
        },
        SET_TOUR_HOME_TAKEN(state, tourDone) {
            state.data.tour_home_taken = tourDone;
        },
        SET_TOUR_PLANNING_TAKEN(state, tourDone) {
            state.data.tour_planning_taken = tourDone;
        },
        
    },
    actions: {
        resetTourData: ({ commit }) => {
            commit('RESET_TOUR_DATA', '');
        },
        setTourHomeTaken({ commit }, tourDone) {
            commit('SET_TOUR_HOME_TAKEN', tourDone);
        },
        setTourPlanningTaken({ commit }, tourDone) {
            commit('SET_TOUR_PLANNING_TAKEN', tourDone);
        }
    },
    getters : {
        getTourHomeTaken: state => state.data.tour_home_taken,
        getTourPlanningTaken: state => state.data.tour_planning_taken,
    }
}