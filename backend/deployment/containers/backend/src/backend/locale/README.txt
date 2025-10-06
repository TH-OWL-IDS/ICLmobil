To generate POT files for translation, run (from the "deployment" directory)

  python3.12 -mvenv ~/venv.iclmobil
  ~/venv.iclmobil/bin/python3 -mpip install -U pip
  ~/venv.iclmobil/bin/python3 -mpip install -U containers/backend/vendor/pyphoton/
  ~/venv.iclmobil/bin/python3 -mpip install -U -r containers/backend/src/requirements.txt

  ~/venv.iclmobil/bin/pybabel extract --keywords="translate_me from_gettext" --output=containers/backend/src/backend/locale/messages.pot containers/backend/src
  ~/venv.iclmobil/bin/pybabel update --init-missing --input-file=containers/backend/src/backend/locale/messages.pot --output-dir=containers/backend/src/backend/locale --locale en_US

After translating in the "containers/backend/src/backend/locale/xx_YY/LC_MESSAGES/messages.po" files:

  ~/venv.iclmobil/bin/pybabel compile --directory=containers/backend/src/backend/locale --statistics --use-fuzzy --locale=en_US

Python gettext does NOT read po files but ONLY mo files!