# Plugins used

ICL-Mobile uses a number of native Cordova plugins to access hardware features.

## Native Plugin Installation

Ruby, gems, cocoapods and some cordova plugins are very problematic, because they might have lots of dependencies. The cordova plugin 'cordova-plugin-push' for instance needs cocoapods to work. Since the version installed on most systems is already outdated, it does not work with any of the latest gems.

Here is what to do on a Mac to get going:

* Install rbenv global before anything else using Homebrew, it's a ruby version manager 
* Open your ~/.bash_profile and check if the following line is in it (if not, add it now)

```bash
#ADDED FOR RUBY
eval "$(rbenv init -)"
```

In order to use this profile before starting the ruby install, do this:

```bash
source ~/.bash_profile
```

* Install the latest version of Ruby-on-Rails and Gem using rbenv
* Make sure the path to ruby is correct using:

```bash
which ruby
```

* Now check if the latest ruby version is used:

```bash
rbenv versions
```

should output something like this:

```bash
  system
  3.1.0
* 3.2.7 (set by /Users/smartinetz/.rbenv/version) <-- this is used!
```

* Install the latest cocoapods version now using ruby gem:

```bash
gem install cocoapods
```

* After the install do this to make sure you got the latest version now:
  
```bash
pod --version
```

Try to recompile the project again and see if it works now.

## Push notifications

The project uses the cordova-plugin-push to handle push notifications in this app. This is the payload needed to send in order for the app to manage them correctly.

### iOS Payload Example

```json
{
  "aps":{
    "alert": {
      "title": "Testing",
      "body": "The text of the alert message"
    },
    "sound":"default",
    "badge":1,
    "content-available": 1,
    "category": "identifier",
    "thread-id": "de.iclowl.iclmobile",
    "sound": "default"
  },
  "notId": 1,
  "pageID": "/wallet"
}
```

### Android Payload Example

```json
{
  "aps":{
    "alert": {
      "title": "Testing",
      "body": "The text of the alert message"
    },
    "sound":"default",
    "badge":1,
    "content-available": 1,
    "category": "identifier",
    "thread-id": "de.iclowl.iclmobile",
    "sound": "default"
  },
  "notId": 1,
  "pageID": "/wallet"
}
```

### Android Firebase Config

To use push notifications on Android, it is necessary to register a Firebase account with Google. After registration, you will receive a configuration file in the form of a JSON file. This file should be copied to the following directory.

```bash
ICL-Frontend/cordova/platforms/android/app/google-services.json
```

## Native Plugins used

Here is a complete list of plugins currently used in this project:

| Plugin         | Link                                                                 |
|----------------|----------------------------------------------------------------------|
| Camera         | <https://github.com/apache/cordova-plugin-camera>                    |
| File           | <https://github.com/apache/cordova-plugin-file>                      |
| File Transfer  | <https://github.com/apache/cordova-plugin-file-transfer>             |
| InAppBrowser   | <https://github.com/apache/cordova-plugin-inappbrowser>              |
| Fingerprint    | <https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio>       |
| Push           | <https://github.com/havesource/cordova-plugin-push>                  |
| Diagnostic     | <https://github.com/dpa99c/cordova-diagnostic-plugin>                |
| Device         | <https://github.com/apache/cordova-plugin-device>                    |
| Vibration      | <https://github.com/apache/cordova-plugin-vibration>                 |
| Haptic         | <https://github.com/wrobins/cordova-plugin-haptic>                   |
| Geolocation    | <https://github.com/apache/cordova-plugin-geolocation>               |
| Android Keyboard | <https://github.com/SinGlEBW/cordova-plugin-android-keyboard>      |

### NPM Plugins used

* [Mapbox](https://github.com/mapbox/mapbox-gl-js)
* [Axios](https://axios-http.com)
* [Chart.js](https://chartjs.org)
* [Mitt](https://github.com/developit/mitt)
* [Swiper](https://swiperjs.com)
* [Vue-ChartJS](https://vue-chartjs.org)
* [Vue-i18n](https://github.com/intlify/vue-i18n)
* [Vuex](https://github.com/vuejs/vuex)
* [Vuex-Persistedstate](https://github.com/robinvdvleuten/vuex-persistedstate)
* [Vuex-Persistedstate-Migrate](https://github.com/grandchef/vuex-persistedstate-migrate)
* [Vue3-Lottie](https://github.com/megasanjay/vue3-lottie)

[Back to Table of Contents](README.md)
