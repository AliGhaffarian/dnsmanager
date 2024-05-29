#!/bin/sh -v



sudo cp dnsmanager.py /bin/dnsmanager
sudo cp dependancies/dnsjumper /bin/dnsjumper
sudo mkdir /etc/dnsmanager
sudo touch /etc/dnsmanager/servers.json
sudo chmod 777 /etc/dnsmanager/servers.json
