# Internationalization (i18n)

The base language is german (`de`).
English (`en`) is available as an alternative language.

## Changing translations for strings in code

See `containers/backend/src/backend/locale/README.txt`.
After those changes, re-build the `backend` container image and restart the container with it.

## Adding a translation language

Adding a language requires several changes on the code level.

Checklist:

- Read `containers/backend/src/backend/locale/README.txt` and add instructions for the new language.
- Add translations for strings according to the `README.txt`.
- Add new language to `settings.py` -> `LANGUAGES`.
- Build and start the `backend` container. Note the error message regarding a missing migration.
- Add the migration to the code, re-build and start the Backend.
