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
        parser = argparse.ArgumentParser()
        parser.parse_args(namespace=self)
    
    def run(self):
        xx = rimuapi.Api()
        # has a cluster id, is active, is master
        existing = xx.orders('N', {'server_type': 'VPS','meta_search': 'com.rimuhosting.kclusterid: com.rimuhosting.kismaster:Y'})
        for order in existing:
            kclusterid = objectpath.Tree(order).execute("$.meta_data[@.key_name is 'com.rimuhosting.kclusterid'].value")
            ip = objectpath.Tree(order).execute("$.allocated_ips.primary_ip")
            #print(order)
            print("Cluster master order_oid:  "  + str(existing[0]["order_oid"]) + " " + list(kclusterid)[0] + " " + ip)
                        
if __name__ == '__main__':
    args = Args();
    args.run()


