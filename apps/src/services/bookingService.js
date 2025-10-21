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
  async getBookings() {
    return axios
      .get(store.getters.getApiHost + store.getters.getApiUrl + '/booking/list/frontend', {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async getBooking(id) {
    return axios
      .get(`${store.getters.getApiHost}${store.getters.getApiUrl}/booking/${id}/frontend`, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async createBooking(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/booking/create', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async tripSearch(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/trip/search/frontend', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async pointsEstimate(data) {
    return axios
      .post(store.getters.getApiHost + store.getters.getApiUrl + '/booking/points/estimate', data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async updateBooking(id, data) {
    return axios
      .patch(`${store.getters.getApiHost}${store.getters.getApiUrl}/booking/update/${id}`, data, {
        headers: {
          Authorization: `Bearer ${store.getters.getUserToken}`
        }
      })
      .then(response => response.data)
      .catch(err => {
        return this.handleError(err);
      });
  },
  async deleteBooking(id) {
    return axios
      .delete(`${store.getters.getApiHost}${store.getters.getApiUrl}/booking/delete/${id}`, {
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