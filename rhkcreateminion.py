import argparse
import os
import json, sys
import urllib.request
from pprint import pprint
from pprint import pformat
import rimuapi
# from jsonpath_rw import jsonpath, parse
import objectpath

isDebug = False
def debug(str):
    if isDebug:
        print(str)
        print()     
class Args(object):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--kclusterid", help="Unique id for this cluster.  e.g. cluster1")
        parser.add_argument("--server_json", required=True, help="Server json.  e.g. containing memory_mb and disk_space_gb.  per http://apidocs.rimuhosting.com/jaxbdocs/com/rimuhosting/rs/order/OSDPrepUtils.NewVPSRequest.html")
        parser.add_argument("--cloud_config", required=True, help="Server cloud config file")
        parser.add_argument("--dc_location", required=False, help="Optional data center location.  e.g. DCDALLAS, DCFRANKFURT, DCAUCKLAND")
        parser.add_argument("--debug", action="store_true", help="Show debug logging")
        parser.parse_args(namespace=self)
        isDebug = self.debug;
    
    def run(self):
        xx = rimuapi.Api()
        server_json = json.load(open(args.server_json))
        debug("server json = " + str(server_json))
        if not hasattr(server_json, "instantiation_options"):
            server_json["instantiation_options"] = dict()
        # if not hasattr(server_json["instantiation_options"], "distro"):
        # required to be a coreos distro
        server_json["instantiation_options"]["distro"] = "coreos.64"
        if not hasattr(server_json["instantiation_options"], "domain_name"):
          server_json["instantiation_options"]["domain_name"] = "coreosminion.localhost"
        if not hasattr(server_json["instantiation_options"], "cloud_config_data"):
           server_json["instantiation_options"]["cloud_config_data"] = open(args.cloud_config).read()
        if not hasattr(server_json, "meta_data"):
            server_json["meta_data"] = list()
        if not hasattr(server_json, "file_injection_data"):
            server_json["file_injection_data"] = list()
        if self.dc_location:
            server_json["dc_location"] = self.dc_location
        # print("server_json=",server_json)
        
        # see if the cluster id is in the server json, else use the command line arg value
        klusterids = objectpath.Tree(server_json).execute("$.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
        if not klusterids is None and len(list(klusterids)) > 0:
            raise Exception("Provide the cluster id as a command line argument.")
        server_json["meta_data"].append({'key_name': 'com.rimuhosting.kclusterid' , 'value' : args.kclusterid})
        server_json["meta_data"].append({'key_name': 'com.rimuhosting.kisminion' , 'value' : 'Y'})
    
        existing = xx.orders('N', {'server_type': 'VPS', 'meta_search': 'com.rimuhosting.kclusterid:' + args.kclusterid + ' com.rimuhosting.kismaster:Y'})
        if len(existing) == 0:
            raise Exception("Could not find that cluster master.  Create the master first?")
        if len(existing) > 1:
            raise Exception("Found multiple cluster masters with this id.  Unexpected.")
        ip = objectpath.Tree(existing).execute("$.allocated_ips.primary_ip")
        if ip is None:
          raise Exception("Could not determine the master node IP.")
        ip=list(ip)[0] 
        
        # replace the magic $kubernetes_master_ipv4 string with the master ip
        server_json["instantiation_options"]["cloud_config_data"] = server_json["instantiation_options"]["cloud_config_data"].replace("$kubernetes_master_ipv4", ip, 99)
        #print("cloud config = " + server_json["instantiation_options"]["cloud_config_data"])

        vm = xx.create(server_json)
        debug ("created minion server: " + str(vm))
                        
if __name__ == '__main__':
    args = Args();
    args.run()


