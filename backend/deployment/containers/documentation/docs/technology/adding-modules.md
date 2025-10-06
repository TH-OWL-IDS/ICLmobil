# Adding or replacing external modules

Beschreibung wie RRive, Email, SharingOS Alternativen (Entwicklungs-Doku, API)

The technology used allows easy addition or replacement of modules.
The needed code changes are outlined below.

## Adding a trip option provider

This could be a different public transport, car pooling or car sharing provider.

The general theme is:

- Leave the models in `models.py` as they are. Extend them using additional fields if needed.
  Note that model changes will result in a needed migration that is output to the container logs on first start
  (which will fail). Grab the output, add it as a migration file to `backend/src/backend/migrations/`
  and rebuild/restart.
- Add periodic synchronization if needed. For tasks that run seldom (like once a day), consider adding the task to
  `backend/src/backend/celery.py` as a function and then wire it to a schedule using `setup_periodic_tasks()`
  (or manually using the UI).
- For frequent (e.g. every few seconds or minutes) periodic tasks, add it to  `backend/src/backend/services.py`
  where they can run as threads along with other tasks.
- Consider adding a diagnostic menu entry. See `backend/src/backend/settings.py` -> `UNFOLD` -> `SIDEBAR`
  on how to add an entry and go from there.
- To add offerings to search results, extend `backend/src/backend/api_v1/trip.py` -> `_search()` with the additional
  option.
- Add tests to `backend/src/backend/tests/` that are run by `manage/run-tests.sh`.
- Modifications in the mobile app might be needed if model or trip option type changes are needed.

## Adding an email provider

- Update configuration in `settings.py` -> `EMAIL_PROVIDER`.
- Update the following places in the code:
  - `backend/src/backend/utils.py` -> `email_setup_problems()`
  - `backend/src/backend/utils.py` -> `send_email_template()`

## Adding an SMS provider

- Replicate the functionality in 
  - `backend/src/backend/twilio.py` -> `create_verification()`
  - `backend/src/backend/twilio.py` -> `get_verify_service()`
  - `backend/src/backend/twilio.py` -> `get_balance()`
  - `backend/src/backend/twilio.py` -> `check_verify_code()`
- Update usage in `backend/src/backend/api_v1/user.py`
- Update usage in `backend/src/backend/views.py`
- Consider adding dedicated diagnostics functionality in the administrative UI.


