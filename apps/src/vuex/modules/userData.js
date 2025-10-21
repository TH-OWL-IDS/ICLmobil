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

import placeholderImage from "@/assets/placeholder/images/profileImagePlaceholder.png";

// User Data Setup
export const userData = {
    state: () => ({
        data: {
            user_id: null,
            user_image: null,
            user_imageUpdatedAt: null,
            user_image_temp_url: null,
            user_image_temp_base64: null,
            user_name: null,
            user_phone: null,
            user_phone_unverified: null,
            user_email: null,
            user_email_unverified: null,
            user_token: null,
            user_statistics: null
        },
        default: {
            data: {
                user_id: null,
                user_image: placeholderImage,
                user_imageUpdatedAt: new Date().getTime(),
                user_image_temp_url: null,
                user_image_temp_base64: null,
                user_name: null,
                user_phone: null,
                user_phone_unverified: null,
                user_email: null,
                user_email_unverified: null,
                user_token: null,
                user_statistics: null
            }
        }
    }),
    mutations: {
        RESET_USER_DATA: state => {
            Object.assign(state.data, state.default.data);
        },
        SET_USER_ID(state, id) {
            state.data.user_id = id;
        },
        SET_USER_IMAGE(state, image) {
            state.data.user_image = image;
        },
        SET_USER_IMAGE_UPDATED_AT(state, updated) {
            state.data.user_imageUpdatedAt = updated;
        },
        SET_USER_IMAGE_TEMP_URL(state, imageURL) {
            state.data.user_image_temp = imageURL;
        },
        SET_USER_IMAGE_TEMP_BASE64(state, imageBase64) {
            state.data.user_image_temp_base64 = imageBase64;
        },
        SET_USER_NAME(state, name) {
            state.data.user_name = name;
        },
        SET_USER_PHONE(state, phone) {
            state.data.user_phone = phone;
        },
        SET_USER_PHONE_UNVERIFIED(state, phone) {
            state.data.user_phone_unverified = phone;
        },
        SET_USER_EMAIL(state, email) {
            state.data.user_email = email;
        },
        SET_USER_EMAIL_UNVERIFIED(state, email) {
            state.data.user_email_unverified = email;
        },
        SET_USER_TOKEN(state, token) {
            state.data.user_token = token;
        },
        SET_USER_STATISTICS(state, statistics) {
            state.data.user_statistics = statistics;
        },
        RESET_USER_TOKEN(state) {
            console.log("USER TOKEN: ", state.data.user_token)
            state.data.user_token = null;
            console.log("USER TOKEN: ", state.data.user_token)
        },
    },
    actions: {
        resetUserData: ({ commit }) => {
            commit('RESET_USER_DATA', '');
        },
        setUserID({ commit }, { id }) {
            commit('SET_USER_ID', id);
        },
        setUserImage({ commit, rootGetters }) {
            let userID = rootGetters['getUserID'];
            let apiImageURL = rootGetters['getApiHost'] + rootGetters['getApiImageUrl'];
            let image = `${apiImageURL}/${userID}`
            commit('SET_USER_IMAGE', image);
        },
        setUserImageUpdatedAt({ commit }, { updated }) {
            commit('SET_USER_IMAGE_UPDATED_AT', updated);
        },
        setUserImageTempUrl({ commit }, { imageURL }) {
            console.log("SETTING USER IMAGE: ", imageURL)
            commit('SET_USER_IMAGE_TEMP_URL', imageURL);
        },
        setUserImageTempBase64({ commit }, { imageBase64 }) {
            commit('SET_USER_IMAGE_TEMP_BASE64', imageBase64);
        },
        setUserImageDefault: ({ commit }) => {
            console.log("SETTING USER IMAGE DEFAULT")
            commit('SET_USER_IMAGE', placeholderImage);
        },
        setUserName({ commit }, { name }) {
            commit('SET_USER_NAME', name);
        },
        setUserPhone({ commit }, { phone }) {
            commit('SET_USER_PHONE', phone);
        },
        setUserPhoneUnverified({ commit }, { phone }) {
            commit('SET_USER_PHONE_UNVERIFIED', phone);
        },
        setUserEmail({ commit }, { email }) {
            commit('SET_USER_EMAIL', email);
        },
        setUserEmailUnverified({ commit }, { email }) {
            commit('SET_USER_EMAIL_UNVERIFIED', email);
        },
        setUserToken({ commit }, { token }) {
            commit('SET_USER_TOKEN', token);
        },
        setUserStatistics({ commit }, { statistics }) {
            commit('SET_USER_STATISTICS', statistics);
        },
        resetUserToken: ({ commit }) => {
            commit('RESET_USER_TOKEN', '');
        },
    },
    getters : {
        getUserID: state => state.data.user_id,
        getUserImage: state => state.data.user_image,
        getUserUpdatedImageAt: state => state.data.user_imageUpdatedAt,
        getUserImageTempUrl: state => state.data.user_image_temp,
        getUserImageTempBase64: state => state.data.user_image_temp_base64,
        getUserName: state => state.data.user_name,
        getUserPhone: state => state.data.user_phone,
        getUserPhoneUnverified: state => state.data.user_phone_unverified,
        getUserEmail: state => state.data.user_email,
        getUserEmailUnverified: state => state.data.user_email_unverified,
        getUserToken: state => state.data.user_token,
        getUserStatistics: state => state.data.user_statistics
    }
}