# Twilio setup

Twilio is used for:

- Mobile phone number verification

To enable this functionality, settings in `.env` need to be filled. Follow this guide to get them:

1. Set up an account at https://login.twilio.com/u/signup
2. Make sure you are logged in
3. Consider signing up for "Nonprofit benefits" here: https://console.twilio.com/us1/billing/nonprofit-benefits/sign-up
4. Add some funds if needed: https://console.twilio.com/us1/billing/manage-billing/billing-overview
5. Set up an API key with token:
   1. Go to https://console.twilio.com/us1/account/keys-credentials/api-keys
   2. In the username drop-down, select "Account management"
   3. Under "Keys & Credentials", select "API keys & tokens"
   4. Under "Region" (top right), make sure the setting is "United States - Default"
   5. Write down the "Account SID" under "Live credentials".
      It is needed for `TWILIO_ACCOUNT_SID` in `.env`.
   6. Next to "API keys - United States (US1) - (recommended)", click "Create API key"
      - Friendly name: `ICL Mobil backend` (suggestion - only used for humans to recognize the usage of the key)
      - Region: United States - Default
      - Key type: Standard
      - Create
   7. Write down the SID and Secret immediately. The secret will not be shown again! 
   8. The SID is needed for `TWILIO_API_SID` in `.env`.
   9. The Secret is needed  for `TWILIO_API_SECRET` in `.env`.
   10. Check the "Got it!" checkbox, click Done
6. Set up a "Verify" account:
   1. Go to https://console.twilio.com/us1/develop/verify/services
   2. Under "Create a service", click "Create new"
   3. Friendly name: "ICL Mobil App" (suggestion - will be shown to users in SMS etc.!)
   4. Click "Read the full statement" and check "Authorize the use of friendly name"
   5. Under "Verification channels", enable "SMS"
   6. Click "Continue"
   7. Keep "Enable Fraud Guard" at "Yes"
   8. Click "Continue"
   9. In the Service settings under "General" look for the "Service SID".
   10. The "Service SID" is needed for `TWILIO_VERIFY_SERVICE_SID` in `.env`.
7. Create a SendGrid (belongs to Twilio) account
   1. Go to https://signup.sendgrid.com/ and follow the signup flow. It should show data from the Twilio account already.
   2. Go to https://app.sendgrid.com/settings/api_keys 
   3. Click "Create API key"
   4. API Key name: "ICL Mobil backend"(suggestion)
   5. Keep "Full access" selected
   6. Click "Create & View"
   7. Copy the long key above the "Done" button
   8. This key is needed for `SENDGRID_API_KEY` in `.env`.
   9. Click "Done"
   10. Go to https://app.sendgrid.com/settings/sender_auth/senders/new
   11. Fill out the form, suggestions:
       1. From Name: ICL e.V.
       2. From Email Adress & Reply To: info@... (this is also needed for `EMAIL_FROM_ADDRESS` in `.env`)
   12. Click "Create"
   13. SendGrid will send an email. Click the button "Verify single sender" in that email.
   14. Click "Return to Single Sender Verification"
8. Create SendGrid templates
   1. Go to https://mc.sendgrid.com/dynamic-templates
   2. Click "Create a dynamic template"
   3. Dynamic Template name: "Reset password email"
   4. Click "Create"
   5. Open dropdown of new template.
   6. Copy "Template ID"
   7. The "Template ID" is needed for `SENDGRID_TEMPLATE_ID_RESET_PASSWORD` (etc.) in `.env`.
   8. Click "Add Version" to add the content (see below for details)
   9. Repear for all templates mentioned below
9. Link SendGrid to Twilio
   1. Go to https://console.twilio.com/ie1/develop/verify/settings/email
   2. Click "Create new email integration"
   3. Integration name: "ICL e.V." (suggestion)
   4. "From" email address: The same as "From Email Address" in SendGrid.
   5. "From" name: ICL e.V. (suggestion)
   6. SendGrid API key: Long key created above


## Sendgrid templates needed

Each type of email needs a template in Sendgrid. It can be styled there as much or little as needed, but there is
some data that needs to be inserted from the backend. This is done using template variables that end up as e.g.
`{{ reset_link }}` in the template.

The following templates are needed:

### `SENDGRID_TEMPLATE_ID_RESET_PASSWORD`: Reset password template

- Template ID goes into `SENDGRID_TEMPLATE_ID_RESET_PASSWORD`.
- Variables used:
  - `{{ reset_code  }}`

Suggested HTML content:
```html
<div style="font-family: inherit; text-align: inherit">Ihr Passwort-Reset-Code lautet: <strong>{{ reset_code }}</strong></div>
<div style="font-family: inherit; text-align: inherit"><br></div>
<div style="font-family: inherit; text-align: inherit">Your password reset code is: <strong>{{ reset_code }}</strong></div>
```

### `SENDGRID_TEMPLATE_ID_VERIFY_EMAIL`: Reset password template

- Template ID goes into `SENDGRID_TEMPLATE_ID_VERIFY_EMAIL`.
- Variables used:
  - `{{ code }}` (legacy)
  - `{{ url }}` (currently used as absolute URI)

### `SENDGRID_TEMPLATE_ID_FEEDBACK`: Email sent to operators when user leaves feedback

- Template ID goes into `SENDGRID_TEMPLATE_ID_FEEDBACK`.
- Variables used:
  - `{{ subject }}`
  - `{{ message }}`
  - `{{ user }}` (Name/email of user)
  - `{{ booking }}` (Booking)
  - `{{ booking_url }}` (Link to backend URL of booking)
  - `{{ vote }}`

