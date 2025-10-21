# ICL Mobile - Change log

## 2.8.2 - 2025-10-01

FIX: Getting images from library caused black screen on some ipads

## 2.8.1 - 2025-09-29

- FIX: Improved iOS purpose strings

## 2.8.0 - 2025-09-17

- Added migration to build RC version

## 2.7.10 - 2025-09-15

- Added tip to favorites on how to edit favorite entries

- Changed favorites not to show home and work address

- FIX: Wrong dialog in planning when no options found
- FIX: Missing handling and dialog for rides out of scope
- FIX: Delete message fails silently
- FIX: Wrong icon used if user action fails in activity view

## 2.7.5 - 2025-09-12

- Added feature to add fixed ride option to favorites to be used for quick start in planning
- Added new native share function to points dialog

- Changed showing user image as icon in toolbar after login
- Changed display text of CO2 emmisions
- Changed max amount of high score and made list scrollable

- FIX: Some small bugs in adding new favorites sheet
- FIX: Display problems in wallet
- FIX: Changed delimiter for german time format from dot to colon
- FIX: Wallet statistics are still showing scooter rides

## 2.5.6 - 2025-08-20

- FIX: Removed all watermarks from animations

## 2.5.5 - 2025-08-18

- Added back gesture for Android
- Added dialog to booking pages if user is not logged in
- Added anchor functionality to accordion list on help page
- Added new point info dialog to ended rides
- Added error dialog if no options could be found
- Added loading animation when opening booking sheet
- Added error message when loading booking page fails
- Added two new API routes to get points from backend
- Added distance and points to all booking dialogs

- Changed maps display in all booking dialogs
- Changed new points dialog to display earned points
- Changed search sheet to open on focus to show search results
- Changed timout for splashscreen animation
- Changed warning icon from circular to triangle
- Changed loading animation for options sheet

- FIX: Navigating from booking dialogs causes errors in planning dialog
- FIX: Missing import in rideOptions leads to error
- FIX: HMTL formated text in accordions is not rendered correctly
- FIX: Problem on home page with scroll to top function
- FIX: Scroll to anchor on help page does not work

## 2.4.0 - 2025-08-08

- Added new edit mode feature for favorites on planning page
- Added new splashscreen animation and eliminated scooter symbol

- Changed scooter icon on home page in segmented control
- Changed scooter booking option, combining scooter and bikes into one
- Changed visibility of search when toggling edit mode

- FIX: Error on planning page causes map to malfunction

## 2.2.0 - 2025-08-04

- Added confetti fx to feedback and ride end functions
- Added latest cordova plugin push

- Change removed icons and made navigation smaller in planning view
- Changed limited console spamming
- Change enabling navbar icons on preferences page
- Changed Android app icons to adaptive icons
  
- FIX: Minor localisation errors
- FIX: Navigation large has wrong property name
- FIX: Login navigation uses wrong property name for large navbar

## 2.1.25 - 2025-07-29

- Added contribution file to project
- Clean up project README
- Changed project documentation language to english
- Changed image processing
- FIX: Verification toast still showing after logout
- FIX: Open keyboard on Android shows toolbar about it

## 2.1.20 - 2025-07-24

- Added e2e testing suite cypress to project
- Added cypress config and custom commands
- Added cypress e2e test for general app functionality
- Added cypress e2e test for home functionalities
- Added cypress e2e test for login functionalities
- Added cypress e2e test for preferences functionalities
- Added cypress e2e test for registration functionalities
- Added cypress e2e test for wallet functionalities
- Added cypress e2e test for activity page
- Added home route to router file for e2e testing

- Added dynamic link URL from backend
- Added frontend project documentation (in progress)
- Added setting remote app settings when app starts

- Changed README with project structure and tech docs
- Changed cypress plugin to latest version
- Changed home page to work with e2e tests
- Changed register page to work with e2e tests
- Changed preferences  page to work with e2e tests
- Changed login page to work with e2e tests
- Changed cypress e2e test for register page
- Changed all activity sheets to work with activity e2e test
- Changed feedback sheet to work with e2e test
- Changed News service backend endpoint

- Changed special and support pages to new system API routes
- Changed app settings to be loaded from backend API
- Changed AppSettingsData extracting settings the user could change into a new file
- Changed appSettings VUEX module to handle remote app config data correctly
- Changed dev mode switch handling to change VUEX data when switching between modes
- Changed phone number validation dialog for easier usage

- FIX: Sheet does not close if ride is canceled by user
- FIX: Intent for RRive Testflight app did not work
- FIX: Error console message using wrong querySelector when using toolbar
- FIX: Direct URLs not loading properly for e2e tests
- FIX: White screen at app start when using browser history on device

## 2.1.6 - 2025-07-14 - HOTFIX

- FIX: Link with car pool app might fail under certain conditions

## 2.1.5 - 2025-07-10

- Changed button behavior for lock and unlock sharing rides

- FIX: Planned rides are not showing in activities
- FIX: Wrong text color in favorites marker when in dark mode
- FIX: Wrong text color in tour dialog when in dark mode
- FIX: Forward only sharing rides to started ride sheet

## 2.1.0 - 2025-07-04

- Added terms checkbox and verification to register page
- Added info popup to display terms on register page
- Added countdown timer to email verification dialog
- Added FAB with scrollUp function for easier navigation
- Added instruction dialog to next and startet rides sheets

- Changed handling and display of all legal pages
- Changed segmented control to always show an active option
- Changed links and text on read more buttons under news
- Changed Android SDK target to latest version 35
- Changed shared ride information to show model and vehicle number
- Changed error handling with email and phone verification
- Changed open started ride sheet after start
- Changed send user to activity view after successful booking
- Changed verification process to be more reliable
- Changed data protection and legal page

- FIX: Only visible options should be listed
- FIX: Planned rides are listed in previous rides

## 2.0.3 - 2025-06-23

- Added location information and a button to fetch all news

## 2.0.2 - 2025-06-18

- Added new VUEX migration patch v202

- Changed car pool dialog to use auth key for app linking
- Changed initial time in ride options dialog from 5 to 10 minutes

- FIX: Wrong property type for active tabs in toolbar component
- FIX: Migration 200 is missing app_version string
- FIX: Messages are missing incoming date and time

## 2.0.0 - 2025-06-16

- Added picker for booking period with shared rides
- Added dev mode badge to app
- Added dev mode toggle to about page
- Added new VUEX migration file

- Changed default app settings data and added production URLs
- Changed API URL for user image in user service lib
- Changed userimage setter API image URL to new format
- Changed takemethere function to work for sharing offers
- Changed statusBar handling
- Changed focus and blur event handling for location search

- FIX: Moved dev badge position to bottom
- FIX: News title has no ellipsis
- FIX: VUEX migration to v190 is not working as expected
- FIX: Default app settings are not set after VUEX migration process
- FIX: Car pool linking not working if user is not logged in
- FIX: Wrong date used when picking rental time
- FIX: Changed string for news category Food & Drinks

## 1.9.25 - 2025-05-28

- Added news category when no item was picked from the segmented control

- Changed from dialogs to toasts in ride options and previous rides
- Changed take me there function for bus and car pool rides

- FIX: Long press handler not working as expected adding favorites to map
- FIX: Empty frame in news when image is missing

## 1.9.20 - 2025-05-21

- Added Face ID toggle to login page
- Added new keyboard plugin for Android

- Changed car pool deep link for ride offers in ride options sheet

- FIX: Minor style changes on wallet page
- FIX: Minor color changes for icons on account page
- FIX: Wrong handling of soft keyboard events on Android
- FIX: Missing back icon in navigation bar
- FIX: Missing case handler for Android at car pool download link
- FIX: Missing check if car pool app was linked before booking
- FIX: Wrong sheet and map height in home and work address sheets
- FIX: Missing default image if user image is missing in backend
- FIX: User gets logged out if Face ID is not used
- FIX: Missing haptic feedback when toggling favorites in map view

## 1.9.7 - 2025-05-13

- Added car pool deep links and UI to next, started and previous ride activities
- Changed car pool deep link to cancel a car pool ride

## 1.9.6 - 2025-05-13 (HOTFIX)

- FIX: Missing NSLocationAlwaysAndWhenInUseUsageDescription string

## 1.9.5 - 2025-05-13

- Added new plugin geolocation for image proof function
- Added a new process to take images as proof after rides
- Added default deep link URLs for car pooling
- Added new preferences page for car pool app
- Added car pool init and booking process
- Added version string dynamically to about page
- Added new migration plugin to keep track of changes

- Changed about page and README content
- Changed README to add migration plugin info

- FIX: Booking button on car pool page was active without login
- FIX: Missing option in data formatter lib for car pool offers
- FIX: Missing event listeners for car pool sheet
- FIX: Last destination sheet remains open when navigating to wallet or prefs
- FIX: Wrong time format in ride options sheet
- FIX: No error message after internal server error in planning

## 1.8.9 - 2025-04-25

- Added new tour slides and animations for planning page
- Added plugin to give haptic feedback to the user
- Added haptic feedback to most interactive app features

- Changed translation strings used for guided tour dialog
- Changed news functionality adding new categories
- Changed looks of news display
- Changed help section to receive content from API
- Changed legal and imprint pages to load content from API
- Changed all Mapbox API calls and URIs to VUEX

- FIX: iPad M4 shows wrong UI theme, delivers false device info
- FIX: Image slot in news is showing even if there is no image
- FIX: Some flaws when editing favorites on planning map

## 1.7.11 - 2025-04-09

- Added animated tour guide slider to home page

- Changed detail information for public transportation
- Changed ticket URL in ticket options
- Changed option to use your own scooter

- Removed old app test data and set new default favorites

- FIX: Experience points need to be floored or ceiled
- FIX: Booking button was still enabled when user was not logged in
- FIX: Empty favorites can be saved and updated
- FIX: Using wrong mapbox APIs when showing directions by foot, bike or scooter
- FIX: Email not found in recovery when using caPs
- FIX: Wrong time format in ride options time picker
- FIX: Using own vehicle is now possible even when no rentals are available

## 1.6.38 - 2025-03-31

- HOTFIX: Opening and closing last destination sheet when adding or editing favorites
- HOTFIX: Refresh map when last destination sheet is opening or closing

## 1.6.36 - 2025-03-31

- Added ride booking to all ride option sheets (shared, public-transportation, car and walk)
- Added new booking page for own vehicles
- Added new link to option list for bikes, scooters and car to use own vehicle
- Added new page to delete user account in app settings
- Added new Forgot-Password page
- Added new list for started rides to activity page
- Added new sheet for started rides
- Added ticket buy option to next and started rides
- Added cancel booking option to next and previous ride sheets
- Added destination field to all ride option sheets
- Added feedback sheet to previous ride sheet
- Added general app feedback sheet to preferences page
- Added distance and map view to foot way sheet
- Added pull-to-refresh to wallet, news and activity pages
- Added dynamic data to CO2 wallet
- Added new plugin diagnostic to handle app settings
- Added new plugins device and vibration to project
- Added plugin vibration to be used on all push notifications
- Added button and hint to map page to navigate user to app settings
- Added auto update of wallet data by login, registrations and app start
- Added graphical ride banner according to ride
- Added disable and enable functions to map views to prevent user errors
- Added new sheet event to handle closing sheets and map cleanup properly
- Added new drawMap function to handle map initialisation
- Added swipeout to previous rides to delete them
- Added new row to display ride departure time
- Added new sheet close event to better handle overall cleanup
- Added and changed tons of translation strings all over the app
- Added overlay graphics for canceled rides
- Added canceled rides to activity view
- Added listener to handle refreshing lists from open sheets
- Added new styles for login and activity pages
- Added new push notification dispatcher
- Added trouble shooting and install section to project README
- Added logic to delete last destinations according to user settings
- Added more precise page padding to most pages and sheets
- Added content to about page

- Changed and added new bot graphics for better looks
- Changed overall styles for bot graphics
- Changed long press event when adding new favourites to map
- Changed Top 5 wallet user ranking looks
- Changed news icons on home page
- Changed information when deleting a trip

- Removed accordion element from foot way sheet

- FIX: Search function on help page wasn't working
- FIX: Problems with status bar on iPhone X, XR and XS
- FIX: Header on login page didn't wrap properly
- FIX: Using InAppBrowser to show ticket page
- FIX: Email was not converted to lowercase when login or registering
- FIX: Wrong end timestamp for started rides
- FIX: Missing translation for activity badges
- FIX: Prevent double count on badges after incoming push notification
- FIX: Emissions not dynamic on account page & wrong translations
- FIX: Calculation of CO2 emmisions
- FIX: Wrong translations in imagepicker component
- FIX: Function to open maps app to get directions
- FIX: Problem with demo data and loading data from API
- FIX: Some statistic and number chrunching bugs in wallet
- FIX: Some bugs and local data storage
- FIX: Function to draw directions on map
- FIX: Destination field value in ride options sheet sometimes empty
- FIX: Data and icon formatter
- FIX: Bug in booking and user service lib when deleting rides
- FIX: Bug in date and time picker in ride options sheet

## 0.9.20 - 2025-02-24

- Added search and display for POIs to map
- Added new route to search for POIs
- Added new handler for search and click handling
- Added plugin for push notifications
- Added reset action to user data VUEX
- Added push token registration to home, login and registration pages
- Added new route to get user data to service
- Added new POI service
- Added new custom filter button to filter POIs
- Added feature to show all favorites as marker on map
- Added feature to quick-edit favorites on the map by drag and drop
- Added feature to quick-place new favorites to map
- Added feature to add new favorite by long press
- Added feature to change favorite by drag and drop
- Added new category for map filter feature to show and hide favorites
- Changed email verification process
- Changed news on home page to news groups
- Changed existing POIs on map to be clickable
- Changed action button to be disabled for home and work favorites
- Changed handling of search querys and selections on map
- Changed and added click handler and new POI data management
- Changed workflow to edit and create home and work favorites
- Changed translations
- Fixed long press problem with touch events on device
- Fixed soft keyboard problem in sheets with data input
- Fixed bug in test data
- Fixed bug to place empty favorite
- Fixed bug to place empty work and home favorites

## 0.8.9 - 2025-01-31

- Added validator component to take care of phone and email validations
- Prepared ride booking to use verify component before final booking step
- Changed code for sticky booking button
- Added new states for temporary user images
- Changed login and registration views to reflect new verification process
- Added new destroy flag for toasts on favorites and messages sheets
- Added toasts to map and planning to inform user about ongoing actions
- Moved message service from home to register and login page
- Changed imagePicker component to store temporary image data
- Changed verification code on account page
- Added translation to image picker action
- Added and changed translations

## 0.8.5 - 2025-01-24

- FIX: Close timeline when sheet is closed
- Changed VUEX getter for messages
- Changed message format in appTestData
- Changed message view and added translations
- Added new message service lib and fetching of messages to home page
- Changed backend route for trip searches
- Changed rideOption view to fully handle backend data
- Added new ride option views to planning page
- Added new dataFormatter util function to VUEX appData module
- Added new trip planning styles for timeline
- Changed app test data for ride options with new data format
- Changed icons in wallet to reflect changes on booking page
- Added new translations for ride booking and options
- Added new data formatter utility function
- Changed existing utility functions to reflect changes in trip structure
- Added new views for each ride option
- Added new banner images for ride detail view
- Added newsService to load news data from API
- Changed data source to use API
- Added new logic to disable ride options
- Added trip search to service handler
- Added trip search logic to planning page
- Added translation to handle phone and email validation process
- Added logic to check and handle phone validation at registration
- Added debouncing to validate emails on server
- Added logic to start email validation after phone validation passes
- Added logic to login to store token in secret keystore on device
- Added logic to check and handle phone and email validation in login
- Added logic for plugin fingerprint-aio to login using biometric features
- Added toolbar hide and show to device keyboard logic
- Added emitter to catch device ready event when app starts
- Changed VUEX actions for storing plugins
- Changed main app view to use emitter in cordova-app.js
- Reset user data in VUEX if user has no valid token
- Removed keyboard logic from main app view
- Added fingerprint/faceid plugin to project
- Added lodash package to project
- Changed personal data sheet implementing backend logic
- Added translations for wrong code and email
- Changed translation for booking button in activity page
- Added vuex data reset call after user logout
- Added verification routes to user service lib
- Added unverified phone and email to VUEX module
- Changed booking links to buttons in activity page
- Added return key event to login page (for convenience)
- Added new translations for personal data changes and dialogs
- FIX: Wrong response in user service lib
- Added css for activity page
- Added new service lib for bookings
- Added cute bot background gfx to activity page if no rides are found
- FIX: Some minor display issues in next and previous ride sheets
- Added new cute bot background graphics to project
- FIX: Problems with date and time picker
- FIX: Wrong localisation with date and time picker
- FIX: User image not showing after login
- FIX: Images have wrong orientation after using the device camera
- Added a few more missing icons on iOS
- Added translations for error dialogs
- Added backend upload logic to imagePicker component
- FIX: Server response handling in main app view
- FIX: Response and error handling in login page
- FIX: Response and error handling in register page
- FIX: routes, server responses and token handling in service lib
- Added timestamp to VUEX to handle image update after successful upload
- Added logout function
- Added user id and user token state to VUEX
- Added login security to handle pages where login is required
- Added listener to handle specific UI changes
- FIX: Keyboard problem with toolbar
- FIX: Multi lang problems in dialogs
- Added image url state to VUEX
- Added app mode getter to handle converting mode state
- FIX: Made faceID toggle responsive
- FIX: Function to toggle app theme mode
- Locked routes where login will be required
- Added translation strings for form validation
- Added new backend services and error handling
- Added user registration and proper form validation
- Added user login and proper form validation
- Added new plugin to validate forms
- FIX: Made ride options responsive
- FIX: Style of search button in map on ride planning page
- FIX: Spaces in wallet statistics and top 5 leader board
- FIX: Swipe back problem on preferences page
- Changed default API HOST and API Image URL
- Changed visibility and style of status bar to match app
- Changed string for for access to location, camera and photo roll
- Added campus relation to VUEX and to default test data
- FIX: Wrong icons used in ride options

## 0.5.1 - 2024-04-12

- FIX: Deactivated continuous auto geo location

## 0.5.0 - 2024-29-11

- Added new plugins to README
- Changed reactivity of wallet data
- Changed test data and added new wallet test data
- Changed spacing at the end of the sheet
- Fixed reactivity for title in preferences when switching language
- Added imagePicker component to pick or take images from camera or photo roll
- Added camera and file-transfer plugins to project
- Fixed problem with user avatar image not changing after upload
- Fixed height problem for last destination sheet on device
- FIXED problem with automatic user geolocation
- Added new default profile image to VUEX
- Prepared app settings VUEX for upcoming plugins
- Fixed avatar icon display problems
- Changed personal static data over to use VUEX data
- Changed user avatar to icon instead of placeholder image
- Added init for wallet and user VUEX data
- Added personal data to VUEX
- Added wallet data to VUEX
- Added VUEX and test data
- Added Changelog to project
- Changed text in all components and pages to use multi language
- Added i18n to project for multi-language management
- Fixed date and time picker closing before new sheets open or close
- Added new Android splashscreen
- Changed app identifier due to incompatibility with Android
- Fixed page transition problem
- Fixed map not resizing an large devices
- Hide status bar on iOS and Android
- Changed some icons and adjusted some splashscreens
- Added splashscreens and icons for iOS and Android
- Fixed map refresh/resize problem when onscreen keyboard closes
- Fixed calls to third party map apps
- Added ios-deployment-target and set it to 12.0 instead of 11.0
- Changed swipe behaviour on ride option date and time picker dialogs
- Added VUEX store to app.vue
- Deleted f7 store from project
- Added new VUEX store to project
- Added new intents to call Apple and Google maps apps
- Added new preferences and permissions for Android and Apple devices
- Added new Android SDK rules
- Fixed map not resizing after virtual keyboard disappears
- Changed wallet page transition
- Deleted old maplibre planning page
- Fixed ICLNews sheet not opening
- Changed import of placeholder images in ICL news list on home screen
- Deleted unused npms and prepared device build commands for devices
- Changed CSP to accept a wider range of protocols
- Fixed error when building for device
- Deleted old map and ride options page backups
- Add build infos to README

## 0.0.1 - 2024-13-11

- First alpha of the app frontend without backend capabilities
