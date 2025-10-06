# Push notifications

## iOS

Push notifications are sent using
[certificate based authentication](https://developer.apple.com/documentation/usernotifications/establishing-a-certificate-based-connection-to-apns)
(not [token based](https://developer.apple.com/documentation/usernotifications/establishing-a-token-based-connection-to-apns)).
The certificate used for this needs to be generated using Xcode on an Apple macOS device.
It must be exported from `My certificates` (NOT system certificates) to a PKCS#12 file, e.g. `Certificate.p12`,
containing both the certificate (as it was signed by Apple) and the key (that was generated along with the CSR
that went to Apple for signing).
The `.p12` file will be encrypted with a password that the Xcode user has to choose and enter while exporting.
In the example below, the password is `123456`.

The certificate will not be in a format directly suited for this software and must be
prepared like this using `openssl`.
This software needs the (not password protected) private key and the certificate concatenated
to one file/string that is expected to be available in the environment variable `APNS_CERTIFICATE_WITH_KEY_PEM`.

The procedure is as follows:

```bash
$ openssl version
OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
$ CERTFILE_IN=Certificates.p12
$ CERTFILE_PASSWORD=123456
$ CERTFILE_OUT=Certificate_with_key.pem
$ openssl pkcs12 -legacy -clcerts -nokeys -out TEMP.pem -password "pass:${CERTFILE_PASSWORD?}" -nodes -in "${CERTFILE_IN?}"
$ openssl pkcs12 -legacy -nocerts -out TEMP.key1 -password "pass:${CERTFILE_PASSWORD?}" -passin "pass:${CERTFILE_PASSWORD?}" -passout:TempPassword -nodes -in "${CERTFILE_IN?}"
$ openssl rsa -in TEMP.key1 -out TEMP.key2 -passin pass:TempPassword
writing RSA key
$ cat TEMP.key2 TEMP.pem > "${CERTFILE_OUT?}"
$ rm TEMP.pem TEMP.key1 TEMP.key2
$ echo APNS_CERTIFICATE_WITH_KEY_PEM=\' && cat "${CERTFILE_OUT?}" && echo \'
APNS_CERTIFICATE_WITH_KEY_PEM='
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDFS2WNkHahDm8g
...
90GCiG5b55nnRsWtXv18Lv8=
-----END PRIVATE KEY-----
Bag Attributes
    friendlyName: Apple Push Services: de.iclowl.iclmobile
    localKeyID: 91 8E 6D BB D2 27 78 19 A1 03 58 FC 01 D3 5E ED 6F E5 5D 0A
subject=UID = de.iclowl.iclmobile, CN = Apple Push Services: de.iclowl.iclmobile, OU = N8767BA72F, O = Innovation Campus Lemgo e.V., C = US
issuer=CN = Apple Worldwide Developer Relations Certification Authority, OU = G4, O = Apple Inc., C = US
-----BEGIN CERTIFICATE-----
MIIGtzCCBZ+gAwIBAgIQf8F3uNgV4xh7gIlXZPWttDANBgkqhkiG9w0BAQsFADB1
...
xoNeEP8c1EzBucEOnWpCKMIJVZUmmlJaiwZeYuXA0CrrlJJshUVqkbllVg==
-----END CERTIFICATE-----
'
```


## Android

Sending push notifications to Android devices requires a setup as described [here](https://www.twilio.com/docs/notify/configure-android-push-notifications)

- Setup a project here: https://console.firebase.google.com/
  - "Create a Firebase project" (or "Create a project")
  - Project name will be shown in the Firebase console
  - "Join the Google Developer Program" can be disabled
  - Google Analytics can be disabled on this project
  - Create Project
  - -> google-services.json muss in App eingebettet werden
- Project Overview -> Gear -> Project settings -> General
  - Click "Android-Button"
  - Android package name must match the app's ID (de.iclowl.iclmobile)
  - "Register app"
  - Download "google-services.json"
  - Next
  - Next to console
- Project Overview -> Gear -> Project settings -> General
  - Under "Your apps" find the one with the Android package name
  - Click "google-services.json" to download it
  - This file needs to be embedded into the Android development environment
- Project Overview -> Gear -> Project settings -> Cloud Messaging
  - In "Firebase Cloud Messaging API (V1)" click "Manage Service Account"
  - Click the email in the table
  - Click "Keys"
  - Click "Add key" -> "Create new key"
  - Choose JSON -> click "Create"
  - Key file is downloaded
  - The content needs to be fed into the environment variable `ANDROID_GCM_SERVICE_ACCOUNT_JSON`
