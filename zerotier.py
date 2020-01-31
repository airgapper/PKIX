# zerotier.py PKIX ZeroTier Python Wrapper
#
# Author: Nate Sales
#
# This file provides safe(ish) wrappers for ZeroTier's HTTP API.

import requests


class Controller:
    def __init__(self, server="localhost:9993"):
        self.server = server

        try:
            with open("/var/lib/zerotier-one/authtoken.secret") as auth_token_file:
                self.auth_token = auth_token_file.read().strip()
        except PermissionError:
            print("\033[91m[⚠]\033[0m Insufficient read permission for \"/var/lib/zerotier-one/authtoken.secret\"")
            exit(1)

        self.headers = {"X-ZT1-Auth": self.auth_token}

    def status(self):
        return requests.get("http://" + self.server + "/status", headers=self.headers).json()

    def create_network(self, name, routes, mtu=2800, private=True):
        _routes = []
        for route in routes:
            _routes.append({"target": route})

        return requests.post("http://" + self.server + "/controller/network/" + self.status()["address"] + "______",
                             json={
                                 "name": name,
                                 "routes": _routes,
                                 "mtu": mtu,
                                 "private": private
                             }, headers=self.headers).json()

    def get_networks(self):
        return requests.get("http://" + self.server + "/controller/network/", headers=self.headers).json()

    def get_routes(self, network_id):
        _routes = []

        for route in requests.get("http://" + self.server + "/controller/network/" + network_id, headers=self.headers).json()["routes"]:
            _routes.append(route["target"])

        return _routes

    def add_route(self, network_id, route):
        _routes = []
        for route in self.get_routes(network_id):
            _routes.append({"target": route})

        _routes.append({"target": route})

        return requests.post("http://" + self.server + "/controller/network/" + network_id, json={"routes": _routes}, headers=self.headers).json()

    def set_routes(self, network_id, routes):
        _routes = []
        for route in routes:
            _routes.append({"target": route})

        return requests.post("http://" + self.server + "/controller/network/" + network_id, json={"routes": _routes}, headers=self.headers).json()

    def delete_network(self, network_id):
        return requests.delete("http://" + self.server + "/controller/network/" + network_id, headers=self.headers).json()

    def delete_all_networks(self):
        for network in self.get_networks():
            self.delete_network(network)

    def get_members(self, network_id):
        return list(requests.get("http://" + self.server + "/controller/network/" + network_id + "/member", headers=self.headers).json().keys())

    def get_member(self, network_id, member_id):
        return requests.get("http://" + self.server + "/controller/network/" + network_id + "/member/" + member_id, headers=self.headers).json()

    def toggle_member_authorization(self, network_id, member_id):
        current_auth_status = self.get_member(network_id, member_id)["authorized"]

        return requests.post("http://" + self.server + "/controller/network/" + network_id + "/member/" + member_id, json={"authorized": not current_auth_status}, headers=self.headers).json()

    def set_member_ip(self, network_id, member_id, ip):
        return requests.post("http://" + self.server + "/controller/network/" + network_id + "/member/" + member_id, json={"ipAssignments": [ip]}, headers=self.headers).json()
