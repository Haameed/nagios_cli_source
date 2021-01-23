#!/usr/bin/python3
import config
import argparse
import sys
import time
import os
import screen_drawer
import data_writer
import Connect_to_db as DB



arguments = argparse.ArgumentParser(description="Nagios command line tools.")
if len(sys.argv) < 2:
    print("You should tell me what to do. use -h/--help to see manual.")
arguments.add_argument("-show", choices=["dbstatus", "workers", "data_writer"], type=str, action="store", help="%(prog)s  -s/--show service", nargs=1)
arguments.add_argument("-set", choices=["customer", "host_template", "service_template", "bandwidth"], type=str, action="store", help="%(prog)s  -e/-set -H hostname -v value", nargs=1)
arguments.add_argument("-Host_name", metavar="node_name", required='-set' in sys.argv, type=str, nargs=1)
arguments.add_argument("-Value", metavar="new value", required='-set' in sys.argv, type=str, nargs='+')
arguments.add_argument("-bulk_import", choices=["b2b", "p2p"], type=str, action="store", help="%(prog)s  -b/--bulk-import", nargs=1)
arguments.add_argument("-input", metavar="inpute_file", required='-bulk_import' in sys.argv, nargs='?', type=argparse.FileType('r'))
args = arguments.parse_args()
is_single_action = True
if args.show:
    if args.set or args.bulk_import:
        is_single_action = False
if args.set:
    if args.show or args.bulk_import:
        is_single_action = False

if args.bulk_import:
    if args.set or args.show:
        is_single_action = False
        pass
if not is_single_action:
    print("please specify only one action. please use -h/--help for more information")
    sys.exit(1)
if args.show:
    if args.show[0] == "dbstatus":
        end_epoch_time = int(round(time.time())) + config.auto_kill_minutes * 60
        while int(round(time.time())) < end_epoch_time:
            try:
                screen_drawer.dbstatus_main()
            except KeyboardInterrupt:
                break
    elif args.show[0] == "workers":
        end_epoch_time = int(round(time.time())) + config.auto_kill_minutes * 60
        while int(round(time.time())) < end_epoch_time:
            try:
                screen_drawer.workers_main()
            except KeyboardInterrupt:
                break

    elif args.show[0] == "data_writer":
        data_writer.get_service_status()
if args.set:
    node_name = args.Host_name[0]
    new_value = args.Value[0]
    
    connection = DB.connect_to_db(config.master_pass, config.db_user, config.db_pass)
    cursor = connection.cursor()
    cursor.execute(f"select exists (select host_name from tbl_host where host_name = '{node_name}')")
    node_status = cursor.fetchone()
    if node_status[0] == 1:
        cursor.execute(f"select id from tbl_host where host_name = '{node_name}'")
        host_id = cursor.fetchone()[0]
    else:
        print(f"node {node_name} doesn't exist. please check for possible typo.")
        sys.exit(1)
    if connection.is_connected():
        if args.set[0] == "customer":
            cursor.execute(f"select exists (select hostgroup_name from tbl_hostgroup where hostgroup_name = '{new_value}')")
            customer_status = cursor.fetchone()
            if customer_status[0] == 1:
                cursor.execute(f"select id,hostgroup_name from tbl_hostgroup where hostgroup_name = '{new_value}'")
                result = cursor.fetchone()
                hostgroup_id = result[0]
                customer_name = result[1]
                cursor.execute(f"select id from tbl_contact where contact_name ='{new_value}'")
                contact_id = cursor.fetchone()[0]
                cursor.execute(f"update tbl_lnkHostToHostgroup set idSlave = {hostgroup_id}  where idMaster = {host_id}")
                cursor.execute(f"update tbl_lnkHostToContact set idSlave = {contact_id} where idMaster = {host_id}")
                cursor.execute(f"update join_ecare_data set contact_name = '{customer_name}' , contact_id = {contact_id} where host_name = '{node_name}'")
                cursor.execute(f"update p2p_join_ecare_data set contact_name = '{customer_name}' , contact_id = {contact_id} where host_name = '{node_name}'")
                cursor.execute(f"update tbl_host set last_modified = NOW() where id = {host_id} ")
                connection.commit()
            else:
                print(f"Customer {new_value} doesn't exist")
                cursor.close()
                connection.close()
                sys.exit(1)
        elif args.set[0] == "host_template":
            cursor.execute(f"select exists (select template_name from tbl_hosttemplate where template_name = '{new_value}')")
            template_status = cursor.fetchone()
            if template_status[0] == 1:
                cursor.execute(f"select id,template_name from tbl_hosttemplate where template_name = '{new_value}'")
                result = cursor.fetchone()
                hosttemplate_id = result[0]
                template_name = result[1]
                cursor.execute(f"update tbl_lnkHostToHosttemplate set idSlave = {hosttemplate_id}  where idMaster = {host_id}")
                cursor.execute(f"update tbl_host set last_modified = NOW() where id = {host_id} ")
                connection.commit()
            else:
                print(f"Could not find any matching template with '{new_value}'")
                cursor.close()
                connection.close()
                sys.exit(1)
        elif args.set[0] == "service_template":
            cursor.execute(f"select exists (select template_name from tbl_servicetemplate where template_name = '{new_value}')")
            template_status = cursor.fetchone()
            if template_status[0] == 1:
                cursor.execute(f"select id,template_name from tbl_servicetemplate where template_name = '{new_value}'")
                result = cursor.fetchone()
                servicetemplate_id = result[0]
                template_name = result[1]
                cursor.execute(f"select id from tbl_service where config_name = '{node_name}'")
                service_id = cursor.fetchone()[0]
                cursor.execute(f"update tbl_lnkServiceToServicetemplate set idSlave = {servicetemplate_id} where idMaster = {service_id}")
                cursor.execute(f"update tbl_service set last_modified = NOW() where id = {service_id} ")
                connection.commit()
            else:
                print(f"Could not find any matching template with '{new_value}'")
                cursor.close()
                connection.close()
                sys.exit(1)
        elif args.set[0] == "bandwidth":
            import string
            value = args.Value
            bw = value[0]
            try:
                metric = string.capwords(value[1])
                new_value = f"{bw} {metric}"
                cursor.execute(f"update join_ecare_data set var_value = '{new_value}' where  var_name = 'SP' and host_name = '{node_name}'")
                connection.commit()
            except IndexError:
                print("incorrect value. value sould be like '20 Kbps' or '2 Mbps'")
                pass
    cursor.close()
    connection.close()
if args.bulk_import:
    if args.bulk_import[0] == "b2b":
        print("b2b bulk import is developing.")
    elif args.bulk_import[0] == "p2p":
        print("p2p bulk import is developing.")
