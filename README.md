a linux command for managing and using different DNS servers faster

usage: dnsmanager [-h] [-d] [-s SERVER] [-a] [-l] [-n NAME]

options:
  -h, --help            show this help message and exit
  -d, --debug           debug logging
  -s SERVER, --server SERVER
                        ip of a server of name of one previously stored if is
                        a list of ips intended for -a/--add_server switch ips
                        need to be separated by commas
  -a, --add_server      store the server
  -l, --list            print all servers
  -n NAME, --name NAME  name of the server for the -a/--add_server switch

examples : 
dnsmanager -s 8.8.8.8 : set the current dns server to 8.8.8.8
dnsmanager -s 8.8.8.8,8.4.4.8 : set the primary dns server to 8.8.8.8 and the
secondary to 8.4.4.8 note : you can as many secondary dns servers as you want
dnsmanager -a -s 8.8.8.8,8.4.4.8 -n google.com : store a dns server with name
google.com and ips of 8.8.8.8 and 8.4.4.8 dnsmanager -s google.com : try to
set a stored dns server named google.com
