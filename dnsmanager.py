import dnsjumper
import ipaddress
import logging
import argparse
import enum
import json
#{
#   name1:{ip1,ip2}
#   name2:{ip3,ip4}
#}

ARE_SERVERS_LOADED : bool = False
SERVERS_JSON_PATH = "conf/servers.json"
PRIMARY_DNS_SET = "setting primary dns server"
PRIMARY_DNS_SET_ERROR = "error during setting server as primary dns"
DNS_ADD = "adding dns"
DNS_ADD_ERROR = "error during adding dns"

def save_server(ips : list[ipaddress.IPv4Address], name : str)->bool:

    if load_server(name) is not None:
        logger.error(f"{name} exists")
        return False

    new_server = {name : ips} 
    SERVERS.append(new_server)

    json_object = json.dumps(SERVERS)
    open(SERVERS_JSON_PATH, "w").write(json_object)
    
    return True

def load_all_servers():
    #load the whole json
    with open(SERVERS_JSON_PATH, "r") as file_to_read: 
        SERVERS = json.load(file_to_read)
        logger.debug(f"loaded json {SERVERS} from file {SERVERS_JSON_PATH}")
    
def load_server(name : str)->list[str]:
    return SERVERS[name] 

def switch_to_server(name)->bool:
    ips : list[str] = load_server(name)

    if ips is None:
        logger.error(f"{name} not found")
        return False
    logger.debug(f"{PRIMARY_DNS_SET} {ips[0]}")

    error_code = dnsjumper.dns_action(ipaddress.IPv4Address(ips[0]), dnsjumper.ACTION.SET_DNS)
    if (error_code):
        logger.error(f"{PRIMARY_DNS_SET_ERROR} {ips[0]} error code : {error_code}")
    
    for ip in ips[1::]:
        error_code = dnsjumper.dns_action(ipaddress.IPv4Address(ip), dnsjumper.ACTION.ADD_DNS)

        logger.debug(f"{DNS_ADD} {ip}")

        if error_code:
            logger.error(f"{DNS_ADD_ERROR} {ip} error_code : {error_code}")
            return False
        
    return True

def resolve_action()->bool:
    try:

        ip = ipaddress.IPv4Address(CONFIG.server[0])
        error_code = dnsjumper.dns_action(ip, dnsjumper.ACTION.SET_DNS)
        logger.debug(f"{PRIMARY_DNS_SET} {ip}") 

        if error_code:
            logger.debug(f"{PRIMARY_DNS_SET_ERROR} {ip}")

        for ip in CONFIG.server[1::]:
            ip = ipaddress.IPv4Address(CONFIG.server[0])
            error_code = dnsjumper.dns_action(ip, dnsjumper.ACTION.ADD_DNS)
            logger.debug(f"{DNS_ADD} {ip}") 

            if error_code:
                logger.debug(f"{DNS_ADD_ERROR} {ip}")

       


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--debug", help="debug logging", action="store_true", default=False)
    parser.add_argument("-s", "--server", help="ip of a server of name of one previously stored if is a list of ips intended for -a/--add_server switch ips need to be separated by commas", required=True)
    parser.add_argument("-a", "--add_server", help="store the server", action="store_true")
    parser.add_argument("-l", "--list", help="print all servers", action="store_true")
    parser.add_argument("-n", "--name", help="name of the server for the -a/--add_server switch")

    

    return parser.parse_args()    


if __name__ == "__main__":
    CONFIG = handle_args()
    

    load_all_servers()

    logger = logging.getLogger()
    if CONFIG.debug:
        logging.basicConfig(level=10)

    logger.debug(CONFIG)

    if CONFIG.list :
        print(SERVERS)
        exit(0)
    
    if CONFIG.add_server:
        if CONFIG.name is None:
            logger.error("no name provided")
            exit(1)

        save_server(CONFIG.server, CONFIG.name)
        exit(0)

    
