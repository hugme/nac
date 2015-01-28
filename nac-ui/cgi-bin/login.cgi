#!/bin/bash

# Set the variables
. $(cat varset)

use_bust_functions
use_base_functions
use_form_functions

unset BARCODE_ERROR LOGIN_ERROR

CONTENT_STRING=$(dd bs=512 count=1 2>/dev/null )
[ -z "$QUERY_STRING" ] && QUERY_STRING=$CONTENT_STRING
for X in  ${QUERY_STRING//&/ }; do
	case $X in
		USERNAME=*) USERNAME=$(echo ${X#*=} | tr [A-Z] [a-z]);;
		PASSWD=*) PASSWD=$(bustit ${X#*=});;
		EMAIL=*) EMAIL=$(bustit ${X#*=});;
		ERROR=*) ERROR=${X#*=};;
		*) ERROR=unexpected variable: $X;;
	esac
done

####################################################################################
# This is where we check the username and password. if it's good we redirect them
# to the authenticated page

echo "Content-type: text/html"

[ -n "$ERROR" ] && {
EXPIRE_YEAR=$((++$(date +%y)+2))
echo "set-cookie: USER=$USERNAME; expires=Sun, 01-Jul-$EXPIRE_YEAR 10:38:00 GMT; path=/cgi-bin/;"
echo "set-cookie: HASH=${RANDOM_HASH}; expires=Sun, 01-Jul-$EXPIRE_YEAR 10:38:00 GMT; path=/cgi-bin/;"
case $ERROR in
	LOGOUT) ERROR="You are successfully logged out";;
	MISMATCH) ERROR="Your login session has expired";;
	*) ERROR="An unknown login error has occured.";;
esac
}

[ -n "$USERNAME" ] && {
  # if there is, check the password
  USER_VRFY=yes
  [[ "${USER_VRFY}" == yes ]] && {
    # set the expiration date
    EXPIRE_YEAR=$((++$(date +%y)+2))
    RANDOM_HASH=$RANDOM$RANDOM$RANDOM$RANDOM
	echo $USERNAME:$RANDOM_HASH >> $ERROR_LOG
    echo "$USERNAME:$RANDOM_HASH" > $LOGGED_IN/$USERNAME 2>> $ERROR_LOG
    echo "set-cookie: USER=$USERNAME; expires=Sun, 30-Sep-$EXPIRE_YEAR 10:38:00 GMT; path=/cgi-bin/;"
    echo "set-cookie: HASH=${RANDOM_HASH}; expires=Sun, 30-Sep-$EXPIRE_YEAR 10:38:00 GMT; path=/cgi-bin/;"
	cat <<- EOF
	
	<html><head>
	<META http-equiv=refresh content="0;URL=/cgi-bin/auth.cgi">
	</head><body></body bgcolor="#404040"></html>
	EOF
  exit 0
  } || {
    LOGIN_ERROR="Login Failed. Please try again."
    ## turn this on for testing only (it shows the password
    #echo "Login_Error $DATE -- $USERNAME - $USER_VRFY - $TEST_HASH" >> $ERROR_LOG
  }
} 

####################################################################################
# Here is the login page. It will print errors if needed

cat << EOF

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
  <link rel="stylesheet" type="text/css" href="/stylesheets/main.css" />
  <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
  <title>NAC UI</title>
 </head>
 <body>
  <div class=top>
   <div class=topinner>
    <h3 class=top>&nbsp; &nbsp;Nagios Alerting Configurator</h3>
    <ul class=top>
     <li class=top></li>
    </ul>
   </div>
  </div>
  <div class=center>
   <div class=menu><img src="/images/nac-top.gif"><p class=menu></p>
    <img src="/images/nac-bottom.jpg">
   </div>
  <div class=content>
	 <p id="error">$ERROR</p>
   <p id="error">$LOGIN_ERROR</p>
   <div class=center>
    <h2>
     This is the Business Services Nagios Administrative Console.<br/>
     Please login using your LDAP credentials.
    </h2>
	  <form method=post action=/cgi-bin/login.cgi>
     <p class=center>
      Username: <input type=TEXT NAME=USERNAME size=14><br>
      Password: <input type=PASSWORD NAME=PASSWD size=14><br>
		  <br>
		  <input type="submit" value="Log In">
  	 </p>
	  </form>
   </div>
  </div>
 </body>
</html>

EOF
exit 0
