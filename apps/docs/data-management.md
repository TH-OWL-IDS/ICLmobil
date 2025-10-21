# Data Management

The app uses a local **Vuex Store** for user, plugin, and session data. Important main data is stored in the backend and only partially transferred to the app.

## Vuex Modules

| Module        | Description                                                                                 |
|---------------|--------------------------------------------------------------------------------------------|
| appData       | News, rides, options, favorites, support texts, push notifications                         |
| appSettings   | Backend API, push token, API URLs, Cordova plugins, language, settings                     |
| tours         | Management of in-app tours                                                                 |
| userData      | UserID, image, name, phone, email, token, statistics                                       |
| walletData    | Rides, distance, duration, emissions, scores, level, points, ranking                       |

**Migrations:**  
Migrations are managed via files in the `/src/vuex/migration/` folder (e.g., `v189.js`, `v190.js`, ...).

[Back to Table of Contents](README.md)
