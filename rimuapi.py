import urllib
import os
from requests import Request, Session

try:
    import json
except ImportError:
    import simplejson as json


def sort_unique(sequence):
    import itertools
    import operator

    return itertools.imap(
        operator.itemgetter(0),
        itertools.groupby(sorted(sequence)))


def valid_domain_name(domain_name):
    import re

    if len(domain_name) > 255:
        return False
    domain_name.rstrip('.')
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in domain_name.split("."))


def load_settings(name, path=None):
    import imp

    path = path or os.getenv('PATH')
    home_dir = os.path.expanduser('~')
    dirs = path.split(os.pathsep)
    dirs.insert(0, home_dir)
    for d in dirs:
        bin_path = os.path.join(d, name)
        if os.path.exists(bin_path):
            f = open(os.path.abspath(bin_path))
            settings = imp.load_source('settings', '', f)
            f.close()
            return settings
    return None


class Api:
    def __init__(self, key=None):
        self._key = key
        self._base_url = 'https://rimuhosting.com'

        self._distros = []
        self._plans = []
        self._orders = []

        if not self._key:
            self._key = os.getenv('RIMUHOSTING_APIKEY', None)
        if not self._key:
            settings = load_settings('.rimuhosting')
            if settings:
                self._key = settings.apikey

    def __send_request(self, url, data=None, method='GET'):
        if self._key:
            headers = {
                'Authorization': "rimuhosting apikey=%s" % self._key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        else:
            raise Exception('Get API Key')
        url = urllib.basejoin(self._base_url, url)

        data = data if isinstance(data, str) else json.dumps(data)

        s = Session()
        req = Request(method, url,
                      data=data,
                      headers=headers
                      )
        prepped = s.prepare_request(req)
        resp = s.send(prepped)
        return resp

    # list available distros
    def distros(self):
        r = self.__send_request('/r/distributions')
        if r.ok:
            data = r.json()
            self._distros = data['get_distros_response']['distro_infos']
            return self._distros
        else:
            raise Exception(r.status_code, r.reason)

    # list pricing plans & data centers
    def plans(self):
        r = self.__send_request('/r/pricing-plans')
        if r.ok:
            data = r.json()
            self._plans = data['get_pricing_plans_response']['pricing_plan_infos']
            return self._plans
        else:
            raise Exception(r.status_code, r.reason)

    def data_centers(self):
        try:
            plans = self._plans
        except AttributeError:
            plans = self.plans()
        data_centers = list(sort_unique([i['offered_at_data_center'] for i in plans]))
        return data_centers

    # list of orders/servers
    def orders(self, include_inactive='N'):
        payload = {'include_inactive': include_inactive}
        r = self.__send_request('/r/orders;%s' % urllib.urlencode(payload))
        if r.ok:
            data = r.json()
            self._orders = data['get_orders_response']['about_orders']
            return self._orders
        else:
            raise Exception(r.status_code, r.reason)

    # create server
    def create(self, domain, **kwargs):
        _options, _params, _req = {}, {}, {}
        if not valid_domain_name(domain):
            raise Exception(418, 'Domain not valid')
        _options['domain_name'] = domain
        if 'password' in kwargs:
            _options['password'] = kwargs['password']
        if 'distro' in kwargs:
            _options['distro'] = kwargs['distro']
        if 'control_panel' in kwargs:
            _options['control_panel'] = kwargs['control_panel']
        if 'disk_space_mb' in kwargs:
            _params['disk_space_mb'] = kwargs['disk_space_mb']
        if 'memory_mb' in kwargs:
            _params['memory_mb'] = kwargs['memory_mb']
        if 'dc_location' in kwargs:
            _req['dc_location'] = kwargs['dc_location']
        if 'meta_data' in kwargs:
            _req['meta_data'] = kwargs['meta_data']
        if 'file_injection_data' in kwargs:
            _req['file_injection_data'] = kwargs['file_injection_data']
        if 'ssh_pub_key' in kwargs:
            _req['file_injection_data'] = []
            _req['file_injection_data'].append(
                {'data_as_string': kwargs['ssh_pub_key'],
                 'path': '/root/.ssh/authorized_keys'})
        _req['instantiation_options'] = _options
        _req['vps_parameters'] = _params
        payload = {'new_order_request': _req}
        r = self.__send_request('/r/orders/new-vps', data=payload, method='POST')
        if r.ok:
            return r.json()
        else:
            raise Exception(r.status_code, r.reason, r.text)

    # reinstall server
    def reinstall(self, domain, order_oid, **kwargs):
        _options, _params, _req = {}, {}, {}
        if not valid_domain_name(domain):
            raise Exception(418, 'Domain not valid')

        _options['domain_name'] = domain
        if 'password' in kwargs:
            _options['password'] = kwargs['password']
        if 'distro' in kwargs:
            _options['distro'] = kwargs['distro']
        if 'control_panel' in kwargs:
            _options['control_panel'] = kwargs['control_panel']
        if 'disk_space_mb' in kwargs:
            _params['disk_space_mb'] = kwargs['disk_space_mb']
        if 'memory_mb' in kwargs:
            _params['memory_mb'] = kwargs['memory_mb']
        if 'dc_location' in kwargs:
            _req['dc_location'] = kwargs['dc_location']
        if 'meta_data' in kwargs:
            _req['meta_data'] = kwargs['meta_data']
        if 'file_injection_data' in kwargs:
            _req['file_injection_data'] = kwargs['file_injection_data']
        if 'ssh_pub_key' in kwargs:
            _req['file_injection_data'] = []
            _req['file_injection_data'].append(
                {'data_as_string': kwargs['ssh_pub_key'],
                 'path': '/root/.ssh/authorized_keys'})
        _req['instantiation_options'] = _options
        _req['vps_parameters'] = _params
        payload = {'new_order_request': _req}
        r = self.__send_request('/r/orders/order-%s-%s/vps/reinstall' % (order_oid, domain),
                                data=payload, method='PUT')
        if r.ok:
            return r.json()
        else:
            raise Exception(r.status_code, r.reason, r.text)

    # check status
    def status(self, domain, order_oid):
        r = self.__send_request('/r/orders/order-%s-%s/vps' % (order_oid, domain))
        if r.ok:
            data = r.json()
            return data['get_vps_status_response']['running_vps_info']
        else:
            raise Exception(r.status_code, r.reason, r.text)

    def info(self, domain, order_oid):
        r = self.__send_request('/r/orders/order-%s-%s' % (order_oid, domain))
        if r.ok:
            data = r.json()
            return data['get_order_response']['about_order']
        else:
            raise Exception(r.status_code, r.reason, r.text)

    def _get_order_oid(self, domain=None, ip=None):
        oids = []
        if domain is None and ip is None:
            return False
        orders = self._orders if self._orders else self.orders()
        for o in orders:
            if o['domain_name'] == domain:
                oids.append(o['order_oid'])
                if ip and ip in o['allocated_ips'].itervalues():
                    return o['order_oid']
        return oids

    # cancel server
    def delete(self, domain, order_oid):
        if not valid_domain_name(domain):
            raise Exception(418, 'Domain not valid')
        else:
            r = self.__send_request('/r/orders/order-%s-%s/vps' % (order_oid, domain),
                                    method='DELETE')
            if r.ok:
                return r.json()
            else:
                raise Exception(r.status_code, r.reason, r.text)

    # change state of server
    # states: RUNNING | NOTRUNNING | RESTARTING | POWERCYCLING
    def change_state(self, domain, order_oid, new_state):
        if not valid_domain_name(domain):
            raise Exception(418, 'Domain not valid')
        r = self.__send_request('/r/orders/order-%s-%s/vps/running-state' % (order_oid, domain),
                                data={'running_state_change_request': {'running_state': new_state}},
                                method='PUT')
        if r.ok:
            return r.json()
        else:
            raise Exception(r.status_code, r.reason)

    def reboot(self, domain, order_oid):
        return self.change_state(domain, order_oid, 'RESTARTING')

    def powercycle(self, domain, order_oid):
        return self.change_state(domain, order_oid, 'POWERCYCLING')

    def start(self, domain, order_oid):
        return self.change_state(domain, order_oid, 'RUNNING')

    # move VPS to another host
    def move(self, domain, order_oid,
             update_dns=False,
             move_reason='',
             pricing_change_option='CHOOSE_BEST_OPTION',  # 'CHOOSE_SAME_RESOURCES' | 'CHOOSE_SAME_PRICING'
             selected_host_server_oid=None):

        if not valid_domain_name(domain):
            raise Exception(418, 'Domain not valid')
        r = self.__send_request('/r/orders/order-%s-%s/vps/host-server' % (order_oid, domain),
                                data={'vps_move_request': {
                                    'is_update_dns': update_dns,
                                    'move_reason': move_reason,
                                    'pricing_change_option': pricing_change_option,
                                    'selected_host_server_oid': selected_host_server_oid}},
                                method='PUT')
        if r.ok:
            return r.json()
        else:
            raise Exception(r.status_code, r.reason)
