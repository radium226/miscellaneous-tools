#!/bin/bash

export SCRIPT_DIR=`dirname "${0}"`
export WEBLOGIC_QUIET="${WEBLOGIC_QUIET:-1}"

weblogic_classpath()
{
	declare classpath=""
	declare jar_fp=
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/Java/DevelopmentKit/1.6.0/lib/tools.jar"`
	classpath="${classpath};${jar_fp}"
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/wlserver/server/lib/weblogic_sp.jar"`
	classpath="${classpath};${jar_fp}"
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/wlserver/server/lib/weblogic.jar"`
	classpath="${classpath};${jar_fp}"
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/modules/features/weblogic.server.modules_10.3.6.0.jar"`
	classpath="${classpath};${jar_fp}"
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/wlserver/server/lib/webservices.jar"`
	classpath="${classpath};${jar_fp}"
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/modules/ORGAPA~1.1/lib/ant-all.jar"`
	classpath="${classpath};${jar_fp}"
	jar_fp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/modules/NETSFA~1.0_1/lib/ant-contrib.jar"`
	classpath="${classpath};${jar_fp}"
	
	echo "${classpath}"
}

weblogic_path()
{
	declare dp=
	declare path=""
	
	dp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/wlserver/server/native/win/32"`
	path=
	
	dp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/wlserver/server/bin"`
	path="${path};${dp}"
	
	dp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/modules/org.apache.ant_1.7.1/bin"`
	path="${path};${dp}"
	
	dp=`cygpath --windows "${SOFTWARES}/Oracle/Java/DevelopmentKit/1.6/jre/bin"`
	path="${path};${dp}"
	
	dp=`cygpath --windows "${SOFTWARES}/Oracle/Java/DevelopmentKit/1.6/bin"`
	path="${path};${dp}"
	
	dp=`cygpath --windows "${SOFTWARES}/Oracle/WebLogic/10.3.6/wlserver/server/native/win/32/oci920_8"`
	path="${path};${dp}"
	
	echo "${path}"
}

weblogic_java()
{
	PATH=`weblogic_path` "${JAVA_HOME}/bin/java" -cp `weblogic_classpath` -Xmx1024m -XX:MaxPermSize="128m" "${@}"
}

weblogic_deployer()
{
	weblogic_java "weblogic.Deployer" `[ ${WEBLOGIC_QUIET} -eq 0 ] && echo "-debug"` "${@}"
	return ${?}
}

weblogic_admin()
{
	weblogic_java "weblogic.Admin" `[ ${WEBLOGIC_QUIET} -eq 0 ] && echo "-debug"` "${@}"
	return ${?}
}

weblogic_get_server_state()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_get_server_state: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_get_server_state: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_get_server_state: The password has not been defined. " >&2
		return 1
	fi
	
	declare server="${4}"
	if [ -z "${server}" ]; then
		echo "weblogic_get_server_state: The server has not been defined. " >&2
		return 1
	fi
	
	weblogic_wlst \
		"${SCRIPT_DIR}/GetServerState.py" \
		"${admin_url}" \
		"${user}" \
		"${password}" \
		"${server}" 2>&1 | awk \
'BEGIN {
	print_line=0
}

$0 == "<BEGIN>" {
	print_line=1
	next
}

$0 == "<END>" {
	print_line=0
	next
}

print_line == 1 {
	printf("%s\n", $0)
}'
	return ${?}
}


weblogic_wait_for_server_state()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_wait_for_server_state: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_wait_for_server_state: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_wait_for_server_state: The password has not been defined. " >&2
		return 1
	fi
	
	declare server="${4}"
	if [ -z "${server}" ]; then
		echo "weblogic_wait_for_server_state: The server has not been defined. " >&2
		return 1
	fi
	
	declare expected_state="${5}"
	if [ -z "${expected_state}" ]; then
		echo "weblogic_wait_for_server_state: The expected state has not been defined. " >&2
		return 1
	fi
	
	declare state=
	while true; do
		sleep 5
		state=$( weblogic_get_server_state "${admin_url}" "${user}" "${password}" "${server}" )
		#echo "state=${state}/expected_state=${expected_state}"
		if [ x"${state}" == x"${expected_state}" ]; then
			break
		fi
	done
}
weblogic_cluster_state()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_start_webapp: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_start_webapp: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_start_webapp: The password has not been defined. " >&2
		return 1
	fi
	
	weblogic_admin \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		"CLUSTERSTATE"
	
	return ${?}
}

weblogic_server_logs()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_server_logs: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_server_logs: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_server_logs: The password has not been defined. " >&2
		return 1
	fi
	
	weblogic_admin \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		"SERVERLOG" \
		$( date -d "5 min ago" +"%Y/%m/%d %H:%M" )
	
	return ${?}
}

weblogic_help()
{
	weblogic_deployer "-help"
	return ${?}
}

weblogic_examples()
{
	weblogic_deployer "-examples"
	return ${?}
}

weblogic_advanced()
{
	weblogic_deployer "-advanced"
	return ${?}
}

main()
{
	declare arguments=`getopt -o "u:p:h:i:t:n:w:s:r:e:" -l "user:,password:,host:,port:,targets:,name:,war:,script:,server:,state:" -n "WebLogic.sh" -- "${@}"`
	eval set -- "${arguments}"
	
	declare user=
	declare password=
	declare host=
	declare port=
	declare nodes=
	declare context=
	declare war=
	while true; do
		case "${1}" in
			"-u"|"--user")
					shift; user="${1}"; shift
				;;
			
			"-p"|"--password")
					shift; password="${1}"; shift
				;;
			
			"-h"|"--host")
					shift; host="${1}"; shift
				;;
				
			"-i"|"--port")
					shift; port="${1}"; shift
				;;
			
			"-t"|"--targets")
					shift; targets="${1}"; shift
				;;
			
			"-n"|"--name")
					shift; name="${1}"; shift
				;;
			
			"-w"|"--war")
					shift; war="${1}"; shift
				;;
			
			"-s"|"--script")
					shift; script="${1}"; shift
				;;
				
			"-s"|"--server")
					shift; server="${1}"; shift
				;;
			
			"-e"|"--state")
					shift; state="${1}"; shift
				;;
			
			"--")
					shift; break
				;;
		esac
	done
	
	declare admin_url="t3://${host}:${port}"
	
	declare action=
	if [ "${#}" -eq 0 ]; then
		echo "main: There is no action defined. " >&2
		return 1
	fi
	
	while true; do
		action="${1}"
		if [ -z "${action}" ]; then
			break;
		fi
		shift
		
		case "${action}" in
			"DeployWebapp")
					weblogic_deploy_webapp "${admin_url}" "${user}" "${password}" "${name}" "${targets}" "${war}"
				;;
				
			"UndeployWebapp")
					weblogic_undeploy_webapp "${admin_url}" "${user}" "${password}" "${name}"
				;;
			
			"DeployLibrary")
					#weblogic_deploy_library "${admin_url}" "${user}" "${password}" "${targets}" "${name}" "${war}"
					echo "main: Not implemented! " >&2
				;;
				
			"UndeployLibrary")
					#weblogic_undeploy_library "${admin_url}" "${user}" "${password}" "${targets}" "${name}" 
					echo "main: Not implemented! " >&2
				;;
				
			"ListWebapps")
					weblogic_list_webapps "${admin_url}" "${user}" "${password}"
				;;
			
			"StartWebapp")
					weblogic_start_webapp "${admin_url}" "${user}" "${password}" "${name}"
				;;
			"StopWebapp")
					weblogic_stop_webapp "${admin_url}" "${user}" "${password}" "${name}"
				;;
			"RestartWebapp")
					weblogic_stop_webapp "${admin_url}" "${user}" "${password}" "${name}"
					weblogic_start_webapp "${admin_url}" "${user}" "${password}" "${name}"
				;;
				
			"GetServerState")
					weblogic_get_server_state "${admin_url}" "${user}" "${password}" "${server}"
				;;
			
			"WaitForServerState")
					weblogic_wait_for_server_state "${admin_url}" "${user}" "${password}" "${server}" "${state}"
				;;
				
			"ShowServerLogs")
					weblogic_server_logs "${admin_url}" "${user}" "${password}" "${server}"
				;;
			
			"Help")
					weblogic_help
					weblogic_examples
					weblogic_advanced
				;;
				
			"WLST")
					weblogic_wlst "${script}"
				;;
			
			*)
					echo "main: The <${action}> action is unknown. " >&2
				;;
		esac
	done
}

weblogic_wlst()
{
	declare script="${1}"
	if [ -z "${script}" ]; then
		weblogic_java "weblogic.WLST"
	else
		if [ ! -f "${script}" ]; then
			echo "weblogic_wlst: Script <${script}> does not exists. " >&2
			return 1
		fi
		shift 
		weblogic_java "weblogic.WLST" $( cygpath --windows "${script}" ) "${@}"
	fi
	
	return ${?}
}

weblogic_deploy_webapp()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_deploy_webapp: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_deploy_webapp: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_deploy_webapp: The password has not been defined. " >&2
		return 1
	fi
	
	declare name="${4}"
	if [ -z "${name}" ]; then
		echo "weblogic_deploy_webapp: The name has not been defined. " >&2
		return 1
	fi
	
	declare targets="${5}"
	if [ -z "${targets}" ]; then
		echo "weblogic_deploy_webapp: The targets are undefined. " >&2
		return 1
	fi
	
	declare war="${6}"
	if [ -z "${war}" ]; then
		echo "weblogic_deploy_webapp: The path of the WAR file has not been defined. " >&2
		return 1
	fi
	
	weblogic_deployer \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		-targets "${targets}" \
		-name "${name}" \
		-source `cygpath --windows "${war}"` \
		-upload \
		-deploy
}

weblogic_undeploy_webapp()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_undeploy_webapp: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_undeploy_webapp: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_undeploy_webapp: The password has not been defined. " >&2
		return 1
	fi
	
	declare name="${4}"
	if [ -z "${name}" ]; then
		echo "weblogic_undeploy_webapp: The name has not been defined. " >&2
		return 1
	fi
	
	weblogic_deployer \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		-name "${name}" \
		-undeploy
}

weblogic_start_webapp()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_start_webapp: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_start_webapp: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_start_webapp: The password has not been defined. " >&2
		return 1
	fi
	
	declare name="${4}"
	if [ -z "${name}" ]; then
		echo "weblogic_start_webapp: The name has not been defined. " >&2
		return 1
	fi
	
	weblogic_deployer \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		-name "${name}" \
		-start
}

weblogic_stop_webapp()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_stop_webapp: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_stop_webapp: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_stop_webapp: The password has not been defined. " >&2
		return 1
	fi
	
	declare name="${4}"
	if [ -z "${name}" ]; then
		echo "weblogic_stop_webapp: The name has not been defined. " >&2
		return 1
	fi
	
	weblogic_deployer \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		-name "${name}" \
		-stop
}

weblogic_list_webapps()
{
	declare admin_url="${1}"
	if [ -z "${admin_url}" ]; then
		echo "weblogic_list_webapps: The URL to administrate WebLogic has not been defined. " >&2
		return 1
	fi
	
	declare user="${2}"
	if [ -z "${user}" ]; then
		echo "weblogic_list_webapps: The user has not been defined. " >&2
		return 1
	fi
	
	declare password="${3}"
	if [ -z "${password}" ]; then
		echo "weblogic_list_webapps: The password has not been defined. " >&2
		return 1
	fi
	
	weblogic_deployer \
		-adminurl "${admin_url}" \
		-username "${user}" \
		-password "${password}" \
		-listapps | awk 'NR > 1 {printf("%s\n", $0)}' | sed '$d' | sed 's,^ *,,g'
}

main "${@}"
