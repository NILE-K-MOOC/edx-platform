#!/bin/sh

#sudo service nginx stop
sudo /edx/bin/supervisorctl stop edxapp: edxapp_worker:

source /edx/app/edxapp/edxapp_env
python -m compileall /edx/app/edxapp/edx-platform/

cd /edx/app/edxapp/edx-platform

sudo /edx/bin/edxapp-update-assets-cms
sudo /edx/bin/edxapp-update-assets-lms


sudo /edx/bin/supervisorctl start edxapp: edxapp_worker:
#sudo service nginx start
