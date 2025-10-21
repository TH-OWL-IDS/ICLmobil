# Building & Deployment

The ICL-Mobile app is available in the **Apple App Store** (iOS) and **Google Play Store** (Android). Alpha and beta tests are conducted via **Apple Testflight** and **Google Play Testing**.

## IMPORTANT NOTICE BEFORE YOU BUILD FOR MOBILE

In order to build for mobile you need to create a new build file inside the cordova root folder.

```bash
cd cordova
touch ./build.json
```

This file should hold all code signing identities for iOS and the keystore path for Android.

You can find the documentation about the build.json here:
<https://cordova.apache.org/docs/en/12.x/guide/platforms/android/#using-buildjson>

## IMPORTANT FOR IOS BUILDS

If you are building for iOS, you MUST have a PAID developer account and a valid Apple provisioning profile and valid certificate for development and publishing. If you don't have any of this, don't bother. ;)

Start iOS building process using:

```bash
npm run build-cordova-ios
```

## IMPORTANT FOR ANDROID BUILDS

If you are building for the Google Play Store, you MUST have a PAID Google developer account and a valid certificate for development and publishing. If you don't have any of this, don't bother. ;)

Before you start building check first the cordova requirements:

```bash
cd cordova
cordova requirements
```

Then build the App for release (BUNDLE):

```bash
npm run build-release-android
```

Or build the App for debug (APK):

```bash
npm run build-debug-android
```

Or build the App for debug and then run it directly on a device:

```bash
npm run run-debug-android-device
```

...you MUST add the following path and environment variables:

### On Windows

Follow the instructions here:
<https://cordova.apache.org/docs/en/10.x/guide/platforms/android/index.html#windows>

### On MacOS

To get Android SDK and AVD you need to install Android Studio first. Then install the homebrew version of Gradle afterwards as well.

Edit your ~/.bash_profile or create a new one and add these lines, but remember to enter the correct paths, user and build-tools version.

```bash
#ADDED FOR CORDOVA
export JAVA_HOME=/usr/local/opt/openjdk@17
export PATH=$JAVA_HOME/bin:$PATH
export ANDROID_HOME=/Users/YOUR_USERNAME/Library/Developer/Xamarin/android-sdk-macosx
export ANDROID_SDK_ROOT=/Users/YOUR_USERNAME/Library/Developer/Xamarin/android-sdk-macosx
export PATH="${PATH}:$ANDROID_HOME/platform-tools/"
export PATH="${PATH}:$ANDROID_HOME/cmdline-tools/latest/bin"
export PATH="${PATH}:$ANDROID_HOME/emulator/"
export GRADLE_HOME=/usr/local/Cellar/gradle/8.11/bin
export PATH="${PATH}:$ANDROID_HOME:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$GRADLE_HOME"
export PATH="${PATH}:$ANDROID_HOME/tools:$ANDROID_HOME/build-tools/30.0.3"
```

Don't forget to do this after you are done adding the above:

```bash
source ~/.bash_profile
```

[Back to Table of Contents](README.md)
