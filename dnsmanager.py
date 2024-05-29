#!/bin/python3
import textwrap
import sys
import ipaddress
import logging
import argparse
import enum
import json
import os



logger = None
ARE_SERVERS_LOADED : bool = False
SERVERS_JSON_PATH = "/etc/dnsmanager/servers.json"
PRIMARY_DNS_SET = "setting primary dns server"
PRIMARY_DNS_SET_ERROR = "error during setting server as primary dns"
DNS_ADD = "adding dns"
DNS_ADD_ERROR = "error during adding dns"
SERVERS : dict ={}

class ACTION:
    SET_DNS = "set_dns"
    ADD_DNS = "add_dns"

def dns_action(ip : str, action : str):
    command  = f"sudo dnsjumper --server {ip} --action {action}"
    logger.debug(command)
    
    error_code = os.system(command)

    return error_code
    
    
def init_conf_files():
    
    error_code = os.system("sudo mkdir /etc/dnsmanager")


    error_code = os.system(f"sudo touch {SERVERS_JSON_PATH}")


    if error_code:
        logger.error(f"error touching {SERVERS_JSON_PATH}")
        exit(error_code)


def save_server(ips : list[ipaddress.IPv4Address], name : str)->bool:

    if load_server(name) is not None:
        logger.error(f"{name} exists")
        return False
    
    

    SERVERS[name] = ips

    for ip in ips:
        if is_valid_ip(ip) == False:
            logger.error(f"{ip} is invalid ip")
            return False

    json_object = json.dumps(SERVERS)
    
    open(SERVERS_JSON_PATH, "w").write(json_object)
    return True

def load_all_servers():
    #load the whole json
    try:
        with open(SERVERS_JSON_PATH, "r") as file_to_read: 
            try:
                global SERVERS
                SERVERS = json.load(file_to_read)
                logger.debug(f"loaded json {SERVERS} from file {SERVERS_JSON_PATH}")
                global ARE_SERVERS_LOADED
                ARE_SERVERS_LOADED = True
            except:
                logger.debug(f"no servers loaded from {SERVERS_JSON_PATH}")
                
                return None
    except:
        init_conf_files()

def is_valid_ip(ip : str)->bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception as e:
        logger.debug(e)
        return False
    
    
def load_server(name : str)->list[str]:
    if ARE_SERVERS_LOADED == False or (name not in SERVERS):
        logger.debug(f"loading no server cuz no server is loaded")
        return None
    return SERVERS[name]

def switch_to_server(name : str)->bool:
    ips : list[str] = load_server(name)
    
    if ips is None:
        logger.error(f"{name} not found")
        return False

    for ip in ips:
        if is_valid_ip(ip) == False:
            logger.error(f"{ip} is invalid")
            return False

    logger.debug(f"loaded from server {name} : {ips}")
    if ips is None:
        logger.error(f"{name} not found")
        return False
    logger.debug(f"{PRIMARY_DNS_SET} {ips[0]}")

    error_code = dns_action(ips[0], ACTION.SET_DNS)
    if (error_code):
        logger.error(f"{PRIMARY_DNS_SET_ERROR} {ips[0]} error code : {error_code}")
    
    for ip in ips[1::]:
        error_code = dns_action(ip, ACTION.ADD_DNS)

        logger.debug(f"{DNS_ADD} {ip}")

        if error_code:
            logger.error(f"{DNS_ADD_ERROR} {ip} error_code : {error_code}")
            return False
        
    return True

def resolve_action()->bool:
    global CONFIG
    logger.debug(f"config inside resolv_action : {CONFIG}")
    if is_valid_ip(CONFIG.server[0]) == False:
        return switch_to_server(CONFIG.server[0])


    error_code = dns_action(CONFIG.server[0], action=ACTION.SET_DNS)
    logger.debug(f"{PRIMARY_DNS_SET} {CONFIG.server[0]}") 

    if error_code:
        logger.debug(f"{PRIMARY_DNS_SET_ERROR} {CONFIG.server[0]}")
        return False

    for ip in CONFIG.server[1::]:

        error_code = dns_action(ip, ACTION.ADD_DNS)
        logger.debug(f"{DNS_ADD} {ip}") 

        if error_code:
            logger.debug(f"{DNS_ADD_ERROR} {ip}")
            return False
    return True

def handle_args():
    
    parser = argparse.ArgumentParser(epilog=textwrap.dedent("""\
            examples :
                        dnsmanager -s 8.8.8.8 : set the current dns server to 8.8.8.8
                        dnsmanager -s 8.8.8.8,8.4.4.8 : set the primary dns server to 8.8.8.8 and the secondary to 8.4.4.8
                        note : you can as many secondary dns servers as you want
                        dnsmanager -a -s 8.8.8.8,8.4.4.8 -n google.com : store a dns server with name google.com and ips of 8.8.8.8 and 8.4.4.8
                        dnsmanager -s google.com : try to set a stored dns server named google.com"""))
    parser.add_argument("-d","--debug", help="debug logging", action="store_true", default=False)
    parser.add_argument("-s", "--server", help="ip of a server of name of one previously stored if is a list of ips intended for -a/--add_server switch ips need to be separated by commas",  type=str)
    parser.add_argument("-a", "--add_server", help="store the server", action="store_true")
    parser.add_argument("-l", "--list", help="print all servers", action="store_true")
    parser.add_argument("-n", "--name", help="name of the server for the -a/--add_server switch")

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)
    
    args = parser.parse_args()    
    if args.server is not None:
        args.server = args.server.split(',')
    return args

def list_servers():
    for key in SERVERS.keys():
        print(key)
        print(SERVERS[key])


if __name__ == "__main__":
    CONFIG = handle_args()
    

    logger = logging.getLogger(__name__)
    if CONFIG.debug:
        logging.basicConfig(level=10)

    load_all_servers()
    logger.debug(CONFIG)

    if CONFIG.list:
        if ARE_SERVERS_LOADED:
            list_servers()
            exit(0)
        else:
            logger.error("no stored servers")
            exit(1)
    
    if CONFIG.add_server:
        if CONFIG.name is None:
            logger.error("no name provided")
            exit(1)
        logger.debug(f"called save_server args : {CONFIG.server}, {CONFIG.name}")

        save_server(CONFIG.server, CONFIG.name)
        exit(0)
    logger.debug(f"resolv_action with {CONFIG}")
    resolve_action() 
