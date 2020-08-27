#!/bin/bash

SCRIPTPATH="$(dirname  "$(readlink -f "${BASH_SOURCE[0]}")")"
cd "$SCRIPTPATH"

hash wget  2>/dev/null || { echo >&2 "Please install wget to continue.";  exit 1; }
hash unzip 2>/dev/null || { echo >&2 "Please install unzip to continue."; exit 1; }

rm -f govuk_frontend.zip
wget https://github.com/alphagov/govuk-frontend/releases/download/v3.7.0/release-v3.7.0.zip \
  -O govuk_frontend.zip

if [ $? -ne 0 ]; then
  echo >&2 "Could not download the frontend release package."
  echo     "Perhaps the package URL may need to be updated?"
  exit 1
fi

rm -rf vulnerable_people_form/static
unzip -o govuk_frontend.zip -d vulnerable_people_form/static

if [ $? -ne 0 ]; then
  echo >&2 "Could not unzip the frontend release package."
  echo     "Perhaps the package is corrupted?"
  exit 1
fi

mv vulnerable_people_form/static/assets/* vulnerable_people_form/static
rm -rf vulnerable_people_form/static/assets
rm -f govuk_frontend.zip

echo "Completed."

