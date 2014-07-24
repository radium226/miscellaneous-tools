datasource_name = "jdbc/abesnard"

jdbc_driver = "oracle.jdbc.OracleDriver"
jdbc_user = "..."
jdbc_password = "..."
jdbc_url = "..."
sql_test = "SELECT * FROM DUAL"

cluster_target = "..."

connect("...", "...", "...")
cd("/JDBCSystemResources")
edit()
startEdit()
cmo.createJDBCSystemResource(datasource_name)

cd("/JDBCSystemResources/" + datasource_name + "/JDBCResource/" + datasource_name)
cmo.setName(datasource_name)

cd("/JDBCSystemResources/" + datasource_name + "/JDBCResource/" + datasource_name + "/JDBCDataSourceParams/" + datasource_name)
set("JNDINames", jarray.array([String(datasource_name)], String)) 

cd("/JDBCSystemResources/" + datasource_name + "/JDBCResource/" + datasource_name + "/JDBCDriverParams/" + datasource_name)
cmo.setUrl(jdbc_url)
cmo.setDriverName(jdbc_driver)
cmo.setPassword(jdbc_password)

cd("/JDBCSystemResources/" + datasource_name + "/JDBCResource/" + datasource_name + "/JDBCConnectionPoolParams/" + datasource_name )
cmo.setTestTableName("SQL " + sql_test)
cd("/JDBCSystemResources/" + datasource_name + "/JDBCResource/" + datasource_name + "/JDBCDriverParams/" + datasource_name + "/Properties/" + datasource_name )
cmo.createProperty("user")

cd("/JDBCSystemResources/" + datasource_name + "/JDBCResource/" + datasource_name + "/JDBCDriverParams/" + datasource_name + "/Properties/" + datasource_name + "/Properties/user")
cmo.setValue(jdbc_user)

cd("/SystemResources/" + datasource_name)
cluster = ObjectName("com.bea:Name=" + cluster_target + ",Type=Cluster")
set("Targets", jarray.array([cluster], ObjectName))

save()
activate()
