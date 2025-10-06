# Brevo.com

Brevo is used to send emails for verification of the user's email address.

## Setup

Account & API key

- Create a user and log in to https://app.brevo.com
- On the top right, open the drop down and select "SMTP & API" -> API (or visit https://app.brevo.com/settings/keys/api)
- Click "Generate a new API key"
  - Suggested name: `iclmobil-backend`
  - Write down the API key. It is needed for `BREVO_API_KEY`.


Add a verified sender

- Visit https://app.brevo.com/senders/list
- Use "Add Sender" to add and verify a sender
- The sender should be noted as "Verified"
- Write down the name (`BREVO_SENDER_NAME`) and email address (`BREVO_SENDER_EMAIL`) of the sender.

Create the templates

- https://app.brevo.com/templates/listing
- Make sure the template is active!

### `BREVO_TEMPLATE_ID_FEEDBACK`: Email sent to operators when user leaves feedback

- Template ID goes into `BREVO_TEMPLATE_ID_FEEDBACK`.
- Variables used:
  - `{{ subject }}`
  - `{{ message }}`
  - `{{ user }}` (Name/email of user)
  - `{{ vote }}`

