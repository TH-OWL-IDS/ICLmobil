# Technology Stack

The ICL-Mobile app is a hybrid mobile application for Apple iOS and Google Android, based on **Apache Cordova**, **Framework7**, and **Vue.js**.

- **Apache Cordova**: Open-source framework for mobile development with HTML5, CSS3, and JavaScript. Enables access to native device features via plugins.
- **Framework7**: UI framework for hybrid apps with a native iOS and Android look.
- **Vue.js**: JavaScript framework for app logic and data handling.

## Project Structure

```plaintext
/
├── assets-src/         # F7 Icons/Splashscreens
├── build/              # F7 cordova build
├── cordova/            # Cordova project files (configs, plugins, ...)
├── cypress/            # Cypress E2E test files and commands
│   ├── downloads/      # Added by cypress plugin automatically
│   ├── e2e/            # All cypress end 2 end test files
│   ├── support/        # Custom commands and other support scripts
├── docs/               # Project documentation
├── public/             # Static files
├── src/                # App sourcecode (Vue, Framework7, etc.)
│   ├── assets/         # Static project assets
│   ├── components/     # Reusable ui-components
│   ├── css/            # CSS styles
│   ├── data/           # Default app data files
│   ├── fonts/          # F7 fonts
│   ├── js/             # Javascript libraries
│   |── locales/        # Language files
│   |── pages/          # Page view files
│   ├── services/       # REST-Service-Module
│   ├── tours/          # Tour slide files
│   ├── vuex/           # State-Management (Store, Module, Migration)
│   └── webfonts/       # Other project font files
├── framework7.json     # F7-configuration
├── package.json        # NPM-configuration
├── postcss.config.js   # PostCSS preset config
└── vite.config.js      # Vite-configuration
```

[Back to Table of Contents](README.md)
