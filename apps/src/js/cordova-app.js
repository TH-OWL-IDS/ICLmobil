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

var cordovaApp = {
  f7: null,
  isInBackground: false,

  /*
  This method hides splashscreen after 2 seconds
  */
  handleSplashscreen: function () {
    window.navigator.splashscreen.hide();
    setTimeout(() => {
        lottie.splashscreen
          .hide()
          .then(_ => console.log('Lottie successfully hid the animation'))
          .catch(_ => console.error('Uh oh, there was an error hiding the animation'));
    }, 4000);
  },
  /*
  This method prevents back button tap to exit from app on android.
  In case there is an opened modal it will close that modal instead.
  In case there is a current view with navigation history, it will go back instead.
  */
  handleAndroidBackButton: function () {
    var f7 = cordovaApp.f7;
    const $ = f7.$;
    if (f7.device.electron) return;

    document.addEventListener(
      'backbutton',
      function (e) {
        if ($('.actions-modal.modal-in').length) {
          f7.actions.close('.actions-modal.modal-in');
          e.preventDefault();
          return false;
        }
        if ($('.dialog.modal-in').length) {
          f7.dialog.close('.dialog.modal-in');
          e.preventDefault();
          return false;
        }
        if ($('.sheet-modal.modal-in').length) {
          f7.sheet.close('.sheet-modal.modal-in');
          e.preventDefault();
          return false;
        }
        if ($('.popover.modal-in').length) {
          f7.popover.close('.popover.modal-in');
          e.preventDefault();
          return false;
        }
        if ($('.popup.modal-in').length) {
          if ($('.popup.modal-in>.view').length) {
            const currentView = f7.views.get('.popup.modal-in>.view');
            if (currentView && currentView.router && currentView.router.history.length > 1) {
              currentView.router.back();
              e.preventDefault();
              return false;
            }
          }
          f7.popup.close('.popup.modal-in');
          e.preventDefault();
          return false;
        }
        if ($('.login-screen.modal-in').length) {
          f7.loginScreen.close('.login-screen.modal-in');
          e.preventDefault();
          return false;
        }

        if ($('.page-current .searchbar-enabled').length) {
          f7.searchbar.disable('.page-current .searchbar-enabled');
          e.preventDefault();
          return false;
        }

        if ($('.page-current .card-expandable.card-opened').length) {
          f7.card.close('.page-current .card-expandable.card-opened');
          e.preventDefault();
          return false;
        }

        const currentView = f7.views.current;
        if (currentView && currentView.router && currentView.router.history.length > 1) {
          currentView.router.back();
          e.preventDefault();
          return false;
        }

        if ($('.panel.panel-in').length) {
          f7.panel.close('.panel.panel-in');
          e.preventDefault();
          return false;
        }

        // Default root-level behavior: exit app to show Android home
        if (navigator && navigator.app && typeof navigator.app.exitApp === 'function') {
          navigator.app.exitApp();
        }
        return false;
      },
      false,
    );
  },
  /*
  This method does the following:
    - provides cross-platform view "shrinking" on keyboard open/close
    - hides keyboard accessory bar for all inputs except where it required
  */
  handleKeyboard: function () {
    var f7 = cordovaApp.f7;
    if (!window.Keyboard || !window.Keyboard.shrinkView || f7.device.electron) return;
    var $ = f7.$;
    window.Keyboard.shrinkView(false);
    window.Keyboard.disableScrollingInShrinkView(true);
    window.Keyboard.hideFormAccessoryBar(true);
    window.addEventListener('keyboardWillShow', () => {
      f7.input.scrollIntoView(document.activeElement, 0, true, true);
    });
    window.addEventListener('keyboardDidShow', () => {
      f7.input.scrollIntoView(document.activeElement, 0, true, true);
    });
    window.addEventListener('keyboardDidHide', () => {
      if (document.activeElement && $(document.activeElement).parents('.messagebar').length) {
        return;
      }
      window.Keyboard.hideFormAccessoryBar(false);
    });
    window.addEventListener('keyboardHeightWillChange', (event) => {
      var keyboardHeight = event.keyboardHeight;

      if (keyboardHeight > 0) {
        // Keyboard is going to be opened
        document.body.style.height = `calc(100% - ${keyboardHeight}px)`;
        $('html').addClass('device-with-keyboard');
        $('#mainToolbar').hide();
      } else {
        // Keyboard is going to be closed
        document.body.style.height = '';
        $('html').removeClass('device-with-keyboard');
        $('#mainToolbar').show();
      }
    });
    $(document).on(
      'touchstart',
      'input, textarea, select',
      function (e) {
        var nodeName = e.target.nodeName.toLowerCase();
        var type = e.target.type;
        var showForTypes = ['datetime-local', 'time', 'date', 'datetime'];
        if (nodeName === 'select' || showForTypes.indexOf(type) >= 0) {
          window.Keyboard.hideFormAccessoryBar(false);
        } else {
          window.Keyboard.hideFormAccessoryBar(true);
        }
      },
      true,
    );
  },
  handleKeyboardAndroid: function () {
    var f7 = cordovaApp.f7;
    var $ = f7.$;
    if (f7.device.android) {
      let AndroidKeyboard = cordova.plugins.AndroidKeyboard;
      AndroidKeyboard.on('keyboard', (data) => {
        var keyboardHeight = data.height;

        if (keyboardHeight > 0) {
          // Keyboard is open
          document.body.style.height = `calc(100% - ${keyboardHeight}px)`;
          $('html').addClass('device-with-keyboard');
          $('#mainToolbar').hide();
        } else {
          // Keyboard is closed
          document.body.style.height = '';
          $('html').removeClass('device-with-keyboard');
          $('#mainToolbar').show();
        }
      });
    }
  },
  handleStatusBar: function (f7, statusbar, device) {
    if (device.model.includes('iPhone10') ||
        device.model.includes('iPhone11')) {
          statusbar.hide();
    }
    if (f7.device.android) {
      statusbar.overlaysWebView(true);
      statusbar.backgroundColorByHexString('#00000000');
      console.log("ANDROID STATUS BAR: ", statusbar)
    }
    statusbar.styleDefault();
  },
  init: function (f7, store, emitter) {
    // Save f7 instance
    cordovaApp.f7 = f7;

    document.addEventListener('deviceready', () => {
      // Handle Android back button
      cordovaApp.handleAndroidBackButton();

      // Handle Splash Screen
      cordovaApp.handleSplashscreen();

      // Handle Keyboard
      cordovaApp.handleKeyboard();
      cordovaApp.handleKeyboardAndroid();

      // Handle StatusBar
      cordovaApp.handleStatusBar(f7, StatusBar, device);

      // Dispatch cordova plugins to VUEX store
      store.dispatch('setStatusBar', StatusBar);
      store.dispatch('setPluginDevice', device);
      store.dispatch('setPluginDiagnostic', cordova.plugins.diagnostic);
      store.dispatch('setPluginInAppBrowser', cordova.InAppBrowser);
      store.dispatch('setPluginCamera', navigator.camera);
      store.dispatch('setPluginFile', cordova.file);
      store.dispatch('setPluginFileTransfer', FileTransfer);
      store.dispatch('setPluginFileUploadOptions', FileUploadOptions);
      store.dispatch('setPluginHaptic', cordova.plugins.hapticPlugin);
      store.dispatch('setPluginGeolocation', navigator.geolocation);

      // Reset old user token when app starts for security reasons
      // INFO: This should be on by default for ALL platforms but faceID 
      // can fail on some Android devices so we need to keep the token untouched
      if (f7.device.ios) {
        store.dispatch('resetUserToken');
      }

      // Check if App is in background or not and set flag accordingly
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            cordovaApp.isInBackground = true;
            console.log('App ist im Hintergrund');
        } else {
            cordovaApp.isInBackground = false;
            console.log('App ist wieder im Vordergrund');
        }
      });

      // Initialise Push Notifications 
      var push = PushNotification.init({
        android: {
          alert: "true",
          clearBadge: true,
          badge: true,
          sound: true
        },
        ios: {
          alert: "true",
          clearBadge: true,
          badge: true,
          sound: true
        }
      });

      // Listen for push service registration
      push.on('registration', function(data) {
        console.log("Device Token:", data.registrationId);
        store.dispatch('setPushToken', { token: data.registrationId } );
      });

      // Listen for push notifications
      push.on('notification', function(data) {
        console.log("Notification Data Received:", data);
        console.log("Additional Data: ", data.additionalData);
        if (data.additionalData.pageID) {
          if (cordovaApp.isInBackground) {
            console.log("App is currently in background, dispatching data and navigating...");
            emitter.emit('navigate-after-push', data.additionalData.pageID);
          } else if (!cordovaApp.isInBackground) {
            console.log("App is running in foreground, dispatching data only!");
            emitter.emit('dispatch-push-data', data.additionalData.pageID);
          }
        }
        push.finish(
          () => {
            console.log('processing of push data is finished');
          },
          () => {
            console.log('something went wrong with push.finish for ID =', data.additionalData.notId);
          },
          data.additionalData.notId
        );
      });

      // Listen for push notification errors
      push.on('error', function(e) {
        console.error("Push notification error:", e);
      });

      // Inform vue that our device is ready and plugins can be used
      emitter.emit('deviceReady', '');
    });
  },
};

export default cordovaApp;
