#!/bin/sh

python manage.py fetch_sos_results
python manage.py fetch_oc_results
python manage.py fetch_lac_results
python manage.py fetch_sbc_results

python manage.py build && python manage.py publish