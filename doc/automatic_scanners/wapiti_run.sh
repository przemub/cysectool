#!/bin/sh
# INFO: You need to disable compulsory authentication in DVWA for it to run.

if [ -z $1 ]
then
	echo "Usage: $0 security_level (low/medium/high/impossible)"
	exit 1
fi

wapiti-getcookie -u http://localhost:8000/ -c cookie.json > /dev/null
sed -i "s/low/$1/g" cookie.json

wapiti -u "http://localhost:8000/" -x http://localhost:8000/login.php -x http://localhost:8000/logout.php -x http://localhost:8000/security.php -m "backup,blindsql,crlf,delay,exec,file,htaccess,methods,nikto,permanentxss,shellshock,sql,ssrf,xss" -f txt --color --flush-session -c cookie.json --scope domain 
# rm cookie.json

