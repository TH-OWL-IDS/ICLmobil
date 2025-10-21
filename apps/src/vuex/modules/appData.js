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

import { formatTime } from '@/js/utilities/timeFormatter';
import { formatDate } from '@/js/utilities/dateFormatter';
import { formatIcon } from '@/js/utilities/iconFormatter';
import { formatData } from '@/js/utilities/dataFormatter';

// App Data Setup
export const appData = {
    state: () => ({
        data: {
            news: [],
            iclNews: null,
            campusNews: null,
            eventNews: null,
            foodNews: null,
            favorites: null,
            lastDestinations: null,
            rideOptions: null,
            nextRides: null,
            previousRides: null,
            messages: null,
            campusRelations: null,
            supportTexts: null,
            specialPages: null,
        },
        default: {
            data: {
                news: [],
                iclNews: AppTestData.ICL_NEWS,
                campusNews: AppTestData.CAMPUS_NEWS,
                eventNews: AppTestData.EVENT_NEWS,
                foodNews: AppTestData.FOOD_NEWS,
                favorites: AppTestData.FAVORITES,
                lastDestinations: AppTestData.LAST_DESTINATIONS,
                rideOptions: AppTestData.RIDE_OPTIONS,
                nextRides: AppTestData.NEXT_RIDES,
                previousRides: AppTestData.PREVIOUS_RIDES,
                messages: AppTestData.MESSAGES,
                campusRelations: AppTestData.CAMPUS_RELATIONS,
                supportTexts: AppTestData.SUPPORT_TEXTS,
                specialPages: AppTestData.SPECIAL_PAGES,
            }
        }
    }),
    mutations: {
        RESET_APP_DATA: state => {
            Object.assign(state.data, state.default.data);
        },
        SET_NEWS(state, news) {
            state.data.news = news;
        },
        SET_ICL_NEWS(state, news) {
            state.data.iclNews = news;
        },
        SET_CAMPUS_NEWS(state, news) {
            state.data.campusNews = news;
        },
        SET_FOOD_NEWS(state, news) {
            state.data.foodNews = news;
        },
        SET_EVENT_NEWS(state, news) {
            state.data.eventNews = news;
        },
        SET_FAVORITES(state, favorites) {
            state.data.favorites = favorites;
        },
        SET_LAST_DESTINATIONS(state, lastDestinations) {
            state.data.lastDestinations = lastDestinations;
        },
        CLEAR_OLD_DESTINATIONS(state, days) {
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - days);        
            state.data.lastDestinations = state.data.lastDestinations.filter(destination => {
                return new Date(destination.added) > cutoffDate;
            });
        },
        SET_RIDE_OPTIONS(state, rideOptions) {
            state.data.rideOptions = rideOptions;
        },
        SET_NEXT_RIDES(state, rides) {
            state.data.nextRides = rides;
        },
        SET_PREVIOUS_RIDES(state, rides) {
            state.data.previousRides = rides;
        },
        SET_MESSAGES(state, messages) {
            state.data.messages = messages;
        },
        SET_CAMPUS_RELATIONS(state, relations) {
            state.data.campusRelations = relations;
        },
        UPDATE_FAVORITE_COORDINATES(state, { id, lat, lng, address }) {
            const favorite = state.data.favorites.find(fav => fav.id === id);
            if (favorite) {
                favorite.address = address;
                favorite.lat = lat;
                favorite.long = lng;
            }
        },
        DELETE_FAVORITE(state, favoriteId) {
            const index = state.data.favorites.findIndex(fav => fav.id === favoriteId.id);
            if (index !== -1) {
                state.data.favorites.splice(index, 1);
            }
        },
        SET_SUPPORT_TEXTS(state, texts) {
            state.data.supportTexts = texts;
        },
        SET_SPECIAL_PAGES(state, pages) {
            state.data.specialPages = pages;
        }
    },
    actions: {
        resetAppData: ({ commit }) => {
            commit('RESET_APP_DATA', '');
        },
        setNews({ commit }, { news }) {
            commit('SET_NEWS', news);
        },
        setIclNews({ commit }, { news }) {
            commit('SET_ICL_NEWS', news);
        },
        setCampusNews({ commit }, { news }) {
            commit('SET_CAMPUS_NEWS', news);
        },
        setFoodNews({ commit }, { news }) {
            commit('SET_FOOD_NEWS', news);
        },
        setEventNews({ commit }, { news }) {
            commit('SET_EVENT_NEWS', news);
        },
        setFavorites({ commit }, { favorites }) {
            commit('SET_FAVORITES', favorites);
        },
        setLastDestinations({ commit }, { lastDestinations }) {
            commit('SET_LAST_DESTINATIONS', lastDestinations);
        },
        clearOldDestinations({ commit }, { days }) {
            commit('CLEAR_OLD_DESTINATIONS', days);
        },
        setRideOptions({ commit }, { rideOptions }) {
            commit('SET_RIDE_OPTIONS', rideOptions);
        },
        setNextRides({ commit }, { rides }) {
            commit('SET_NEXT_RIDES', rides);
        },
        setPreviousRides({ commit }, { rides }) {
            commit('SET_PREVIOUS_RIDES', rides);
        },
        setMessages({ commit }, { messages }) {
            commit('SET_MESSAGES', messages);
        },
        setCampusRelations({ commit }, { relations }) {
            commit('SET_CAMPUS_RELATIONS', relations);
        },
        updateFavoriteCoordinates({ commit }, { id, lat, lng, address }) {
            commit('UPDATE_FAVORITE_COORDINATES', { id, lat, lng, address });
        },
        deleteFavorite({ commit }, favoriteId) {
            commit('DELETE_FAVORITE', favoriteId);
        },
        setSupportTexts({ commit }, texts) {
            commit('SET_SUPPORT_TEXTS', texts);
        },
        setSpecialPages({ commit }, pages) {
            commit('SET_SPECIAL_PAGES', pages);
        }
    },
    getters : {
        getNews: state => state.data.news,
        getIclNews: state => state.data.iclNews,
        getCampusNews: state => state.data.campusNews,
        getEventNews: state => state.data.eventNews,
        getFoodNews: state => state.data.foodNews,
        getFavorites: state => state.data.favorites,
        getLastDestinations: state => state.data.lastDestinations,
        getRideOptions: (state) => (locale) =>
            state.data.rideOptions.map((ride) => ({
              ...ride,
              rideDate: formatDate(ride.rideTimestamp, locale),
              rideTimestamp: formatTime(ride.rideTimestamp, locale),
              approxTimeOfArrival: formatTime(ride.approxTimeOfArrival, locale),
              vehicleType: formatData(ride),
              distanceM: Math.ceil(ride.distanceM),
              rideIcon: formatIcon(ride.rideIcon)
            })),
        getRideOptionsUnformated: (state) => state.data.rideOptions,
        getNextRides: (state) => (locale) => {
            const allRides = [...state.data.previousRides, ...state.data.nextRides];

            return allRides
                .filter(ride => ride.state === 'planned')
                .slice()
                .sort((a, b) => new Date(a.rideStartTimestamp) - new Date(b.rideStartTimestamp))
                .map((ride) => ({
                    ...ride,
                    rideDate: formatDate(ride.rideStartTimestamp, locale),
                    rideTime: formatTime(ride.rideStartTimestamp, locale),
                    approxTimeOfArrival: formatTime(ride.rideEndTimestamp, locale),
                    rideIcon: formatIcon(ride.rideIcon)
                }));
        },
        getStartedRides: (state) => (locale) => {
            const allRides = [...state.data.previousRides, ...state.data.nextRides];

            return allRides
                .filter(ride => ride.state === 'started')
                .slice()
                .sort((a, b) => new Date(b.rideStartTimestamp) - new Date(a.rideStartTimestamp))
                .map((ride) => ({
                    ...ride,
                    rideDate: formatDate(ride.rideStartTimestamp, locale),
                    rideTime: formatTime(ride.rideStartTimestamp, locale),
                    approxTimeOfArrival: formatTime(ride.rideEndTimestamp, locale),
                    rideIcon: formatIcon(ride.rideIcon)
                }));
        },
        getPreviousRides: (state) => (locale) => {
            return state.data.previousRides
                .filter(ride => ride.state === 'finished' || 
                        ride.state === 'timeout' || 
                        ride.state === 'canceled')
                .slice()
                .sort((a, b) => new Date(b.rideStartTimestamp) - new Date(a.rideStartTimestamp))
                .map((ride) => ({
                    ...ride,
                    rideDate: formatDate(ride.rideStartTimestamp, locale),
                    rideTime: formatTime(ride.rideStartTimestamp, locale),
                    approxTimeOfArrival: formatTime(ride.rideEndTimestamp, locale),
                    rideIcon: formatIcon(ride.rideIcon)
                }));
        },
        getMessages: (state) => (locale) =>
            state.data.messages.map((message) => ({
                ...message,
                createdAt: formatDate(message.createdAt, locale),
            })),
        getMessagesUnformated: state => state.data.messages,
        getCampusRelations: state => state.data.campusRelations,
        getSupportTexts: state => state.data.supportTexts,
        getSpecialPages: state => state.data.specialPages
    }
}