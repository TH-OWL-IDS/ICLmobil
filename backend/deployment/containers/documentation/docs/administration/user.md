# User

Users are used in two places:

- Administrative users: When logging in to the administration UI (`/admin-backend/`). In this case, the `Username` field is used.
- Normal users: When logging in using the mobile app. In this case, the `Email address` field is used for the username.

## Administrative vs. normal users

Administrative users are allowed login to the administration UI, if

1. they are `Active` and
2. they have the right password and
3. they have `Staff status` and
4. to do anything useful, they need to have `Superuser status`.

Normal users are allowed login using the mobile app, if

1. they are `Active` and
2. they have the right password.

## User details and fields

- **Category**: Set using the mobile app
- **Last name**: Set using the mobile app. The first name is not used.
- **Email address**: Used to log in using the app. This is also where the "reset password" email is sent to.
- **New unverified email address**: Used to temporarily store the email address the user enters when changing
  their email address.
- **Email is verified**: If enabled, the Email address field is considered to contain a verified address.
- **Mobile number verified** and unverified along with the switch: Same mechanism as with the email address.

Permissions:

- **Active**: If disabled, the user cannot log in using the app (or at the administrative UI) anymore.
- **Staff status**: Needed for logging in to the administrative UI.
- **Superuser status**: Needed to do most operations in the administrative UI.

Points and experience:

- **Score points** and **Score experience**: Automatically calculated and updated from bookings.

Misc:

- **Auth key external service**: Internal random value that is passed from the app to the car pooling provider.
  They in turn use it to authenticate when reporting a link state.
- **Pooling is linked**: Once the mobile app sends a user to the car pooling app and the user is set up there,
  the provider calls this backend to report this state. This leads to the mobile app to show the apps as linked.

## Additonal functionality

On top of a user's details view, there are several buttons:

- **Start mobile phone verification (send SMS)**: Immediately triggers sending a verification SMS to that user.
- **Start email verification**: Immediately triggers sending a verification email to that user.
- **Image feedback**: See a list of images that the user uploaded as part of a completed booking.
- **Push notification tokens**: See a list of push notification tokens that the mobile app(s) of the user reported.
  Used for debugging push notification problems.
- **Score**: See a list of rules used for calculating the experience and point scores along with a breakdown of how
  the user's current values were calculated.
- **History**: As in most places in the administrative UI, shows a list of changes regarding this use.

