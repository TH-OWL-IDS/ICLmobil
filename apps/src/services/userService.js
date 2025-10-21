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

import axios from 'axios';
import { store } from '@/vuex/store';

export default {
  async isTokenValid() {
    return axios
      .get(store.getters.getApiHost + store.getters.getApiUrl + '/user/isTokenValid', {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async getUserData() {
    return axios
      .get(store.getters.getApiHost + store.getters.getApiUrl + '/user/getUserData', {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async checkUserImage(userID) {
    return axios
      .get(store.getters.getApiHost + store.getters.getApiImageUrl + '/' + userID, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async getCampusRelations() {
    return axios
      .get(store.getters.getApiHost + store.getters.getApiUrl + '/user/category')
      .then(response => response.data)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async getUserStatistics() {
    return axios
      .get(store.getters.getApiHost + store.getters.getApiUrl + '/user/statistics', {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async login(credentials) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/login', credentials)
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async logout() {
    return axios
      .put(store.getters.getApiHost + store.getters.getApiUrl + '/user/logout', null, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async recover(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/recover', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async reset(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/reset', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async register(credentials) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/register', credentials)
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async validateEmail(credentials) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/validateEmail', credentials)
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async startPhoneNumberVerification() {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/startPhoneNumberVerification', null, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async checkPhoneNumberVerificationCode(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/checkPhoneNumberVerificationCode', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async startEmailVerification() {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/startEmailVerification', null, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async checkEmailVerificationCode(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/checkEmailVerificationCode', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async checkPassword(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/checkPassword', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async updateUser(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/updateUser', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async uploadUserImage(imageData) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/uploadProfileImage', imageData, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async uploadImageProof(imageData) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/uploadImageProof', imageData, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async feedback(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/user/feedback', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async deleteUser() {
    return axios
      .delete(`${store.getters.getApiHost}${store.getters.getApiUrl}/user/deleteUser`, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response.data)
      .catch(err => {
        return this.handleError(err);
      });
  },
  // --------------------------------------------------------------------------
  // ---> OTHER HELPER FUNCTIONS
  // --------------------------------------------------------------------------
  handleError(error) {
    if (error.response) {
      console.log("Error response received from server:");
      console.log("Status code:", error.response.status);
      console.log("Response data:", error.response.data);
      return { msg: "ERROR", status: error.response.status, data: error.response.data };
    } else if (error.request) {
      console.log("No response received:");
      console.log(error.request);
      return { msg: "ERROR", status: "444", data: "Keine Antwort vom Server!" };
    } else {
      console.log("Error setting up the request:");
      console.log('Error', error.message);
      return { msg: "ERROR", status: "500", data: "Die Anfrage konnte nicht bearbeitet werden!" };
    }
  }
};