if [ -z "$1" ]
then
  echo "user_email is null"
else
  echo "user_email is $1"
fi

if [ -z "$2" ]
then
  echo "user_pw is null"
else
  echo "user_pw is $2"
fi

if [ -z "$3" ]
then
  echo "user_name is null"
else
  echo "user_name is $3"
fi

sudo -u www-data /edx/bin/python.edxapp /edx/app/edxapp/edx-platform/manage.py lms --settings devstack create_user -p $2 -e $1 -u $3
