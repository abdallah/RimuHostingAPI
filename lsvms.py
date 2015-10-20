import argparse
import os
import json,sys
import urllib.request
from pprint import pprint
from pprint import pformat
import rimuapi
#from jsonpath_rw import jsonpath, parse
import objectpath

class Args(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description="Provide a listing of all servers associated with this RimuHosting API key")
        parser.parse_args(namespace=self)
    def _getSimplifiedOrder(self, order):
        details = objectpath.Tree(order) 
        ip = details.execute("$.allocated_ips.primary_ip")
        #print(pformat(order))
        summary = {"order_oid" : order["order_oid"]
                   , "primary_ip" : "" if ip is None else ip
                   , "domain_name" : order["domain_name"]
                   , "dc_location" : order["location"]["data_center_location_code"], "running_state" : order["running_state"], "memory_mb" : details.execute("$.vps_parameters.memory_mb"), "order_description" : details.execute("$.order_description") }
        return summary
    
    def serverList(self):
        xx = rimuapi.Api()
        # has a cluster id, is active, is master
        existing = xx.orders('N', {'server_type': 'VPS'})
        output = {}
        output["servers"]=[]
        for order in existing:
            output["servers"].append(self._getSimplifiedOrder(order))
        
        print(pformat(output))
                        
if __name__ == '__main__':
    args = Args();
    args.serverList()


