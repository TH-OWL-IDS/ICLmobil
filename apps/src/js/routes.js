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

import HomePage from '../pages/home.vue';
import TripPlanning from '../pages/planning.vue';
import Activity from '../pages/activity.vue';
import Account from '../pages/account.vue';
import Login from '../pages/login.vue';
import Register from '../pages/register.vue';
import Help from '../pages/help.vue';
import Legal from '../pages/legal.vue';
import Wallet from '../pages/wallet.vue';
import Imprint from '../pages/imprint.vue';
import About from '../pages/about.vue';
import Preferences from '../pages/preferences.vue';
import Favorites from '../pages/favorites.vue';
import Messages from '../pages/messages.vue';

import CarPoolSetup from '../pages/carPoolSetup.vue';
import DataProtection from '../pages/dataProtection.vue';
import DeleteAccount from '../pages/deleteAccount.vue';

var routes = [
  {
    path: '/',
    component: HomePage,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/home',
    component: HomePage,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/planning',
    component: TripPlanning,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/activity',
    component: Activity,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/account',
    component: Account,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/login',
    component: Login,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/register',
    component: Register,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/wallet',
    component: Wallet,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/preferences',
    component: Preferences,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/carPoolSetup',
    component: CarPoolSetup,
    meta: {
      requiresAuth: false
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/dataProtection',
    component: DataProtection,
    meta: {
      requiresAuth: false
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/deleteAccount',
    component: DeleteAccount,
    meta: {
      requiresAuth: true
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/help',
    component: Help,
    meta: {
      requiresAuth: false
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/legal',
    component: Legal,
    meta: {
      requiresAuth: false
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/imprint',
    component: Imprint,
    meta: {
      requiresAuth: false
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/about',
    component: About,
    meta: {
      requiresAuth: false
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/favorites',
    component: Favorites,
    meta: {
      requiresAuth: true
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
  {
    path: '/messages',
    component: Messages,
    meta: {
      requiresAuth: true
    },
    options: {
      animate: true,
      transition: 'f7-push'
    },
  },
];

export default routes;
