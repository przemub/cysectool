#!/bin/sh
# INFO: You need to disable compulsory authentication in DVWA for it to run.

wapiti -u "http://localhost:8000/" -x http://localhost:8000/login.php -m "backup,blindsql,buster,crlf,delay,exec,file,htaccess,methods,nikto,permanentxss,shellshock,sql,ssrf,xss" -f txt --color
