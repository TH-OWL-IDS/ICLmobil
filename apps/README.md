# ICL Mobile

This app is using NodeJS v18.x or higher so please make sure you follow the installation guide in this file.

## License

The Project is running under the [Apache License 2.0](LICENSE)

## Documentation

Check out the project documentation here: [docs/README.md](docs/README.md)

## Changelog

Check out the changelog here: [CHANGELOG.md](CHANGELOG.md)

## Architecture Overview

Check out our documentation for more details: [app-architecture](docs/app-architecture.md)

## Installation

Before you start, make sure you have **Node.js v18.x or higher** installed on your system. We recommend using [Node Version Manager (NVM)](https://github.com/nvm-sh/nvm) to manage your Node.js versions to avoid any trouble.

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ICL-Frontend.git
cd ICL-Frontend
```

### 2. Install Dependencies

Install all required dependencies:

```bash
npm install
```

### 3. NPM Scripts

* 🔥 `start` - run development server
* 🔧 `dev` - run development server
* 🔧 `build` - build web app for production
* 📱 `build-cordova` - build cordova app
* 📱 `build-cordova-ios` - build cordova iOS app
* 📱 `cordova-ios` - run dev build cordova iOS app
* 📱 `build-debug-android` - build cordova debug Android app
* 📱 `build-release-android` - build cordova release bundle Android app
* 📱 `run-debug-android-device` - run dev build cordova Android app on device

## Vite

There is a [Vite](https://vitejs.dev) bundler setup. It compiles and bundles all "front-end" resources. You should work only with files located in `/src` folder. Vite config located in `vite.config.js`.

## Cordova

The Cordova project is located in the `cordova` folder. You shouldn't modify content of `cordova/www` folder. Its content will be correctly generated when you call `npm run cordova-build-prod`.

## Assets

Assets (icons, splash screens) source images located in `assets-src` folder. To generate your own icons and splash screen images, you will need to replace all assets in this directory with your own images (pay attention to image size and format), and run the following command in the project directory:

```bash
framework7 assets
```

Or launch UI where you will be able to change icons and splash screens:

```bash
framework7 assets --ui
```

## Building and Deployment

You can find building and deployment instructions in the [documentation](docs/deployment.md).

## Trouble Shooting

* For native plugin issues, see [docs/plugins.md](docs/plugins.md).

* For Node.js/NPM issues, ensure you are using Node.js 18.x and your dependencies are up to date.

* For push notification setup, see [docs/plugins.md](docs/plugins.md).

## Contribution Guide

Pull Requests are very welcome!
Please follow our [Contribution Guide](CONTRIBUTING.md) for this.

## Tests

The project includes e2e tests with cypress. Test scripts are located in the following folder:

```bash
/cypress/e2e
```

To run any of these tests, open cypress and follow the given instructions:

```bash
npx cypress open
```

## Other Documentation & Resources

* [Framework7 Core Documentation](https://framework7.io/docs/)
* [Framework7 Vue Documentation](https://framework7.io/vue/)
* [Framework7 Icons Reference](https://framework7.io/icons/)
* [Framework7 Community Forum](https://forum.framework7.io)
