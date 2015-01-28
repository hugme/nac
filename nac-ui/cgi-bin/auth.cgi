#!/bin/bash

# Set the variables
. $(cat varset)

use_base_functions

##########################################################
# set your date
EXPIRE_YEAR=$(($(date +%y)+2))

##########################################################
# Look at the cookie and set the variables accordingly
for X in ${HTTP_COOKIE//;/ } ;do
	case ${X%=*} in
		USER)
			USERNAME=${X#*=}
			IFS=":" read USERNAME CURR_HASH USER_ID <<< "$(cat $LOGGED_IN/$USERNAME)"
			export USERNAME;;
		HASH) USER_HASH=${X#*=};;
	esac
done

##########################################################
## SET THE CONTENT AND QUERY STINGS
export CONTENT_STRING=$(dd bs=1024 count=100 2>/dev/null)
[ -z "$QUERY_STRING" ] && QUERY_STRING=$CONTENT_STRING

for X in ${QUERY_STRING//&/ }; do
	case $X in
		CAT=*) CAT=${X#*=};;
		TYPE=*) TYPE=${X#*=};;
		SCR=*) SCR=${X#*=};;
		BARCODE_SEARCH=*) BARCODE_SEARCH=${X#*=};;
	esac
done

# if there is a script, set the CAT and TYPE variables yourself
[ ! -z "$SCR" ] && IFS="|" read -r _ _ CAT TYPE _ <<< "$(grep "^$SCR|" $MENU_ITEMS)"

##########################################################
# Test for truth and redirect if needed, otherwise set
# your cookies or logout if that's what they want
	#echo "test $CURR_HASH==$USER_HASH" >> /tmp/lgerr
	#echo >> /tmp/lgerr
[ -z "$CURR_HASH" -o -z "$USER_HASH" ] && LOGIN_ERROR="EXPIRED"
[ "$CURR_HASH" != "$USER_HASH" ] && {
	LOGIN_ERROR="MISMATCH"
	echo $HTTP_COOKIE >> $ERROR_LOG
}
[ "$SCR" = "LOGOUT" ] && LOGIN_ERROR="LOGOUT"

echo "Content-type: text/html"

[ ! -z "$LOGIN_ERROR" ] && {
	echo
       	echo "<html><head>"
	echo "<META http-equiv=refresh content=\"0;URL=/cgi-bin/login.cgi?ERROR=$LOGIN_ERROR\">"
  echo "<title>NAC</title>"
	echo "</head><body></body></html>"
	exit 0
} || {
	#RANDOM_HASH=$RANDOM$RANDOM$RANDOM$RANDOM
	RANDOM_HASH=$USER_HASH
	#echo $USERNAME:$RANDOM_HASH:$USER_ID > $LOGGED_IN/$USERNAME
	echo "set-cookie: USER=$USERNAME; expires=Sun, 30-Sep-$EXPIRE_YEAR 10:38:00 GMT; path=/cgi-bin/;"
	echo "set-cookie: HASH=$RANDOM_HASH; expires=Sun, 30-Sep-$EXPIRE_YEAR 10:38:00 GMT; path=/cgi-bin/;"
	echo
}


##########################################################
##########################################################
##### Set the admin levels and print the page!! ##########
##########################################################
##########################################################


show_buttons() {
cat << EOF
    <div class=top3>
	<a class=icon href="$URL?SCR=activate_profile" onmouseover="moverav()" onmouseout="moutav()" onClick="clav()"><img class=icon src=/buttons/activate.gif title="Activate a user" id="av"></a>
	<a class=icon href="$URL?SCR=user_inout" onmouseover="moverci()" onmouseout="moutci()" onClick="clci()"><img class=icon src=/buttons/checkin.gif title="Check user in or out" id="ci"></a>
	<a class=icon href="$URL?SCR=view_inout" onmouseover="movervc()" onmouseout="moutvc()" onClick="clvc()"><img class=icon src=/buttons/view_checkin.gif title="View Checkins" id="vc"></a>
	<a class=icon href="$URL?SCR=lost_and_found" onmouseover="moverlf()" onmouseout="moutlf()" onClick="cllf()"><img class=icon src=/buttons/lost_n_found.gif title="Lost and found" id="lf"></a>
	<a class=icon href="$ADMIN_TICKET_URL" onmouseover="moverai()" onmouseout="moutai()" onClick="clai()" target="_blank"><img class=icon src="/buttons/tickets.gif" title="Tickets" id="ai"></a>
    </div>
EOF
}

ADMIN_INFO_FULL=$(grep "^$USERNAME|" $ADMIN_FILE)
[ -z "$ADMIN_INFO_FULL" ] && ADMIN_INFO_FULL="$USERNAME|0|0|0|0|0|0"
IFS="|" read _ USER_LEVEL ADMIN _ <<< "$ADMIN_INFO_FULL"
NONE=0
IFS="|" read _ _ CURR_MENU_TYPE CURR_MENU_CAT CURR_SCRIPT_LEVEL _ <<< "$(grep "^$SCR|" $MENU_ITEMS)"
IFS="|" read -r _ _ CURR_CAT_LEVEL _ <<< "$(grep "$CURR_MENU_TYPE|$CURR_MENU_CAT" $MENU_CATS)"
[ -z "$SCR" ] && {
	IFS=" " read CURR_MENU_TYPE CURR_MENU_CAT CURR_SCRIPT_LEVEL  <<< "NONE NONE 0"
	SCR=home
	}


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
	<li class=top><a class=top href="/cgi-bin/auth.cgi?SCR=LOGOUT">Logout</a></li>
	<!-- <li class=top><a class=top href="/cgi-bin/auth.cgi?SCR=view_account">Account</a></li> -->
	<li class=top><a class=top href="/cgi-bin/auth.cgi?SCR=view_my_profile">Profile</a></li>
	<li class=top><a class=top href="/cgi-bin/auth.cgi">Home</a></li>
    </ul>
    </div>
</div>

<div class=center>
    <div class=menu><img src="/images/nac-top.gif"><p class=menu>

$( [[ $CHECKIN -ge 2 ]] && {
echo "<form method=POST action=/cgi-bin/auth.cgi>
	<input type=text name=BARCODE_SEARCH>
</form>" ; } )

    Hello $USERNAME<br><br>
    $( LAST_MENU_CAT=NONE
    while IFS="|" read MENU_SCRIPT MENU_NAME MENU_TYPE MENU_CAT SCRIPT_LEVEL _ ; do
	### I think I'm pulling some variables twice, check here
	[ ! "$MENU_CAT" = "$LAST_MENU_CAT" ] && {
	    IFS="|" read -r PRIV_NAME _ CAT_LEVEL _ <<< "$(grep "$MENU_TYPE|$MENU_CAT" $MENU_CATS)"
	    [ ! -z "$MENU_NAME" -a "${!PRIV_NAME}" -ge "$CAT_LEVEL" ] && {
		sed -n "/$MENU_TYPE|$MENU_CAT/s/.*|.*|.*|\(.*\)/\1/p" $MENU_CATS
		echo "<br>"
	    }
	}
	[ ! -z "$MENU_NAME" -a "${!PRIV_NAME}" -ge "$SCRIPT_LEVEL" ] && {
	    echo "&nbsp&nbsp&nbsp&nbsp <a class=menu href=\"/cgi-bin/auth.cgi?SCR=$MENU_SCRIPT\">$MENU_NAME</a><br>"
	}
	LAST_MENU_CAT="$MENU_CAT"
	done< <(sed '/^#/d;/^$/d' $MENU_ITEMS ) )

    </p>
    <img src="/images/nac-bottom.jpg">
    </div>
    <div class=content>

    $( [ ! -x "$BIN_DIR/$SCR" ] && SCRIPT_ERROR="This script does not exist"
############ I have no idea why this has to be in here twice
############ But if you take one out it will break everything
    IFS="|" read _ SCR_NAME SCR_TYPE SCR_CAT SCRIPT_LEVEL _ <<< "$(grep "^$SCR|" "$MENU_ITEMS")"
    IFS="|" read _ SCR_NAME SCR_TYPE SCR_CAT SCRIPT_LEVEL _ <<< "$(grep "^$SCR|" "$MENU_ITEMS")"
    #echo "=$TESTME===$SCRIPT_LEVEL===$SCR_TYPE==$SCR==="
    # if there is no script level check the invisable script list, then user goes home

    [ -z "$SCRIPT_LEVEL" ] && {
	IFS="|" read SCR_NAME SCR_TYPE SCRIPT_LEVEL _  <<< "$(grep "^$SCR|" "$INVISABLE_MENU_ITEMS" )"
	[ -z "$SCRIPT_LEVEL" ] && {
	    SCRIPT_LEVEL=0
	    SCR_TYPE=NONE
	    SCR=home
	}
    }
    [ "$SCRIPT_LEVEL" -gt "${!SCR_TYPE}" ] && {
	SCRIPT_ERROR="Your login is not permitted to run this script"
	}
    [ -z "$SCRIPT_ERROR" ] && {
	echo "$QUERY_STRING" | $BIN_DIR/$SCR $USER_ID
    } || {
	# go back to check the cat and script levels
	echo "<p id="error">$SCRIPT_ERROR</p>"
	echo "$(date) $USERNAME ERROR-$SCRIPT_ERROR at string $QUERY_STRING" >> $ERROR_LOG
    } )
	
	</div>
</div>

</body>
</html>
EOF
