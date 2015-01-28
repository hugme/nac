#!/bin/bash

# Set the variables
. $(cat varset)
MY_KEY=kS21xpg2xLx1r9sOXUiNcXCXFJIOqAWA
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
i=0
for X in  ${QUERY_STRING//&/ }; do
 case $X in
  CAT=*) CAT=${X#*=};;
  TYPE=*) TYPE=${X#*=};;
  SCR=*) SCR=${X#*=};;
  DO=*) DO=${X#*=};;
  DEL=*) DEL=${X#*=};;
  OBJ=*) OBJ=${X#*=};;
  ATT=*) ATT[i]="${X#*=}"
         i=$(($i+1));;
  HEAD=*) HEAD=${X#*=};;
  KEY=*) KEY=${X#*=};;
 esac
done
[[ $HEAD == NO ]] && EOL="<br>"

case $DEL in
 TAB) D='&#9;';;
 PIPE) D='|';;
 SIMI) D=';';;
 COMMA) D=',';;
 *) D='|';DEL="PIPE";;
esac


# if there is a script, set the CAT and TYPE variables yourself
[ ! -z "$SCR" ] && IFS="|" read -r _ _ CAT TYPE _ <<< "$(grep "^$SCR|" $MENU_ITEMS)"

##########################################################
# Test for truth and redirect if needed, otherwise set
# your cookies or logout if that's what they want
[[ $KEY != $MY_KEY ]] && {
 [ -z "$CURR_HASH" -o -z "$USER_HASH" ] && LOGIN_ERROR="EXPIRED"
 [ "$CURR_HASH" != "$USER_HASH" ] && {
 	LOGIN_ERROR="MISMATCH"
 }
 [ "$SCR" = "LOGOUT" ] && LOGIN_ERROR="LOGOUT"
 
 
 [ ! -z "$LOGIN_ERROR" ] && {
  echo "Content-type: text/html"
 	echo
        	echo "<html><head>"
  #echo "$KEY -- $MY_KEY"
  #echo $QUERY_STRING
 	echo "<META http-equiv=refresh content=\"0;URL=/cgi-bin/login.cgi?ERROR=$LOGIN_ERROR\">"
  echo "<title>NAC</title>"
 	echo "</head><body></body></html>"
 	exit 0
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
}
################################################################################
## From here down is where you download the file
################################################################################

[ -z "$ERROR" ] && {
cat << EOF
content-disposition: form-data; name="Business Report"; filename="ice_report.csv"
set-cookie: HASH=$USER_HASH; expires=$EXPIRE_DATE; path=/cgi-bin/attendees/;
set-cookie: INFO=$ADMIN_LEVEL; expires=$EXPIRE_DATE; path=/cgi-bin/attendees/;
Content-type: text/$FILE_TYPE

EOF

 case $OBJ in
  ##########################################################################
  #### First lets work on the role
  ##########################################################################
  ROLE)
   TABLE="role R"
   i=0
   for E in ${ATT[@]} ; do
    [[ $E == role_name ]] && {
     CALL[i]=NAME
     COL[i]="R.name"
     HEAD[i++]="Role Name${D}"
     }
    [[ $E == role_services ]] && {
     CALL[i]=SERVICES
     while IFS="|" read ID NAME _ ; do
      SERVICE_NAME[ID]=$NAME
     done< <(echo "select service_id,name from services;" | sql_query)
     COL[i]="R.services"
     HEAD[i++]="Role Services${D}"
     }
    [[ $E == role_host ]] && {
     CALL[i]=HOST
     while IFS="|" read S_ID ONE_HOST ONE_ROLE _ ; do
      HOST_NAME[S_ID]=$ONE_HOST
      HOST_ROLE[S_ID]=$ONE_ROLE
     done< <(echo "select server_id,hostname,role from servers;" | sql_query)
     COL[i]="R.role_id"
     HEAD[i++]="Host Template${D}"
     }
    [[ $E == role_esc ]] && {
     CALL[i]=ESC
     COL[i]="R.escalations"
     HEAD[i++]="Escalations${D}"
     }
    [[ $E == role_dep ]] && {
     CALL[i]=DEP
     COL[i]="R.deps"
     HEAD[i++]="Dependancies${D}"
     }
   done

   echo "${HEAD[@]}$EOL"
   while read DATA ; do
    IFS="|" EDATA=($DATA)
     for i in ${!COL[@]} ; do
      [[ $i != 0 ]] && printf "${D}"
      case ${CALL[i]} in
       SERVICES) printf "\""
        IFS=" "; for X in ${EDATA[i]}; do printf "${SERVICE_NAME[X]} " ; done
        printf "\"";;
       HOST) printf "\""
        for THIS_HOST in ${!HOST_ROLE[@]}; do [[ ${HOST_ROLE[THIS_HOST]} == ${EDATA[i]} ]] && printf "${HOST_NAME[THIS_HOST]} " ; done
        printf "\"";;
       *) printf "\"${EDATA[i]}\"" ;;
      esac
     done
     echo "$EOL"
   done< <( echo "select $(echo ${COL[@]}|tr " " ,) from $TABLE;" | sql_query )
   #echo "select $(echo ${COL[@]}|tr " " ,) from $TABLE;"
  ;;

  ##########################################################################
  #### Now the services
  ##########################################################################
  SERVICE)
   TABLE="services S"
   i=0
   for E in ${ATT[@]} ; do
    [[ $E == srv_name ]] && {
     CALL[i]=NAME
     COL[i]="S.name"
     HEAD[i++]="Service Name${D}"
    }
    [[ $E == srv_hosts ]] && {
     CALL[i]=HOSTS
     while IFS="|" read S_ID ONE_HOSTNAME ONE_SERVICES _ ; do
      H_HOSTNAME[S_ID]=$ONE_HOSTNAME
      H_SERVICES[S_ID]=$ONE_SERVICES
     done< <(echo "select S.server_id,S.hostname,R.services from servers S, role R where R.role_id=S.role;" | sql_query)
     COL[i]="S.service_id"
     HEAD[i++]="Hosts${D}"
    }
    [[ $E == srv_roles ]] && {
     CALL[i]=ROLES
     while IFS="|" read R_ID ONE_ROLE ONE_SERVICES _ ; do
      SERVICE_ROLE[R_ID]=$ONE_ROLE
      SERVICE_SERVICES[R_ID]=$ONE_SERVICES
     done< <(echo "select role_id,name,services from role;" | sql_query)
     COL[i]="S.service_id"
     HEAD[i++]="Roles${D}"
    }
    [[ $E == srv_desc ]] && {
     CALL[i]=DESC
     COL[i]="S.description"
     HEAD[i++]="Description${D}"
    }
    [[ $E == srv_temp ]] && {
     CALL[i]=TEMP
     COL[i]="S.use"
     HEAD[i++]="Templates${D}"
    }
    [[ $E == srv_check_command ]] && {
     CALL[i]=CKCMD
     COL[i]="S.check_command"
     HEAD[i++]="Check Commands${D}"
    }
    [[ $E == srv_build_name ]] && {
     CALL[i]=BLDNM
     COL[i]="S.build_name"
     HEAD[i++]="Build Name${D}"
    }
    [[ $E == srv_url ]] && {
     CALL[i]=URL
     COL[i]="S.notes_url"
     HEAD[i++]="URL${D}"
    }
    [[ $E == srv_notes ]] && {
     CALL[i]=NOTE
     COL[i]="S.nag_notes"
     HEAD[i++]="Internal Notes${D}"
    }
    [[ $E == srv_loc ]] && {
     CALL[i]=LOC
     COL[i]="S.location"
     HEAD[i++]="Location${D}"
    }
   done

   echo "${HEAD[@]}$EOL"
   while read DATA ; do
    IFS="|" EDATA=($DATA)
    for i in ${!COL[@]} ; do
     [[ $i != 0 ]] && printf "${D}"
     case ${CALL[i]} in
       HOSTS) printf "\""
         for THIS_HOST in ${!H_HOSTNAME[@]}; do [[ ${H_SERVICES[THIS_HOST]} == *" ${EDATA[i]} "* || ${H_SERVICES[THIS_HOST]} == "${EDATA[i]} "* || ${H_SERVICES[THIS_HOST]} == *" ${EDATA[i]}" || ${H_SERVICES[THIS_HOST]} == "${EDATA[i]}" ]] && printf "${H_HOSTNAME[THIS_HOST]} " ; done
        printf "\"";;
       ROLES) printf "\""
        #for THIS_ROLE in ${!SERVICE_SERVICES[@]}; do [[ ${SERVICE_SERVICES[THIS_ROLE]} == ${EDATA[i]} ]] && printf "${SERVICE_ROLE[THIS_HOST]} " ; done
        for THIS_ROLE in ${!SERVICE_SERVICES[@]}; do [[ ${SERVICE_SERVICES[THIS_ROLE]} == *" ${EDATA[i]} "* || ${SERVICE_SERVICES[THIS_ROLE]} == "${EDATA[i]} "* || ${SERVICE_SERVICES[THIS_ROLE]} == *" ${EDATA[i]}" || ${SERVICE_SERVICES[THIS_ROLE]} == "${EDATA[i]}" ]] && printf "${SERVICE_ROLE[THIS_ROLE]} " ; done
        printf "\"";;
      *) printf "\"${EDATA[i]}\"" ;;
     esac
    done
    echo "$EOL"
   done< <( echo "select $(echo ${COL[@]}|tr " " ,) from $TABLE $WHERE;" | sql_query )
   echo "select $(echo ${COL[@]}|tr " " ,) from $TABLE $WHERE;"

   #echo "Service ID${D}Service Name${D}Service Description${D}Templates${D}Check Command${D}Name to build${D}Service Groups${D}Notes${D}URL${D}Internal Notes${D}Location<br>"
   #while IFS="|" read SRV_ID SRV_NAME SRV_DESC SRV_USE SRV_CHECK SRV_BUILD SRV_GROUPS SRV_NOTES SRV_URL SRV_INTNOTES SRV_LOCATION _ ; do
   # echo "\"$SRV_ID\"${D}\"$SRV_NAME\"${D}\"$SRV_DESC\"${D}\"$SRV_USE\"${D}\"$SRV_CHECK\"${D}\"$SRV_BUILD\"${D}\"$SRV_GROUPS\"${D}\"$SRV_NOTES\"${D}\"$SRV_URL\"${D}\"$SRV_INTNOTES\"${D}\"$SRV_LOCATION\"<br>"
   #done< <(echo "select service_id,name,description,use,check_command,build_name,service_groups,nag_notes,notes_url,int_notes,location from services;" | sql_query)
  ;;

  ##########################################################################
  #### Finally the Hosts
  ##########################################################################
  HOST)
   TABLE="servers V"
   i=0
   for E in ${ATT[@]} ; do
    [[ $E == hst_name ]] && {
     CALL[i]=NAME
     COL[i]="V.hostname"
     HEAD[i++]="Hostname${D}"
    }
    [[ $E == hst_role ]] && {
     CALL[i]=ROLE
     COL[i]="R.name"
     HEAD[i++]="Role${D}"
     TABLE="$TABLE, role R"
     [[ -z $WHERE ]] && WHERE="R.role_id=V.role" || WHERE="$WHERE and R.role_id=V.role"
    }
   done
   [[ -n $WHERE ]] && WHERE="where $WHERE"

   echo "${HEAD[@]}$EOL"
   while read DATA ; do
    IFS="|" EDATA=($DATA)
    for i in ${!COL[@]} ; do
     [[ $i != 0 ]] && printf "${D}"
     case ${CALL[i]} in
      *) printf "\"${EDATA[i]}\"" ;;
     esac
    done
    echo "$EOL"
   done< <( echo "select $(echo ${COL[@]}|tr " " ,) from $TABLE $WHERE;" | sql_query )
   echo "select $(echo ${COL[@]}|tr " " ,) from $TABLE $WHERE;"
  ;;
 esac

}
exit 0

