# pkix.py PKIX utilities and HTML templating
#
# Author: Nate Sales
#
# This file provides PKIX utils for PeeringDB and RADb, as well as HTML template builders

import requests

controller = None

# Decodes ASN from IPv6 address
def ip_to_asn(ip):
    ip = ip.split(":")[1:]

    asn = ""

    for i in ip:
        if i[0] != "f":
            asn += i[0]

    return asn

# Encodes ASN into an IPv6 address
def asn_to_ip(asn):

    if len(asn) > 7:
        print("ASN overflows 32bit integer.")
        exit(1)

    ip = "fd00:"

    for chr in asn + (7 - len(asn)) * 'f':
        ip += chr + "fff:"

    return ip.strip(":")

# TODO: Possibly deprecate this.
# # Get "desc" attribute from ASN in RADb
# def asn_desc(asn):
#     asn = "AS" + str(asn)
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect(("whois.radb.net", 43))
#         s.sendall((asn + " -T aut-num\r\n").encode())
#         data = s.recv(4096)
#
#         for line in data.decode().split("\n"):
#             if line.startswith("descr"):
#                 return line.replace("descr:", "").lstrip()


def get_asn_name_set(asn):
    raw = requests.get("https://peeringdb.com/api/net?asn=" + str(asn)).json()["data"][0]

    try:
        name = raw["name"]
    except KeyError:
        name = None

    try:
        as_set = raw["irr_as_set"].split(" ")[0]

        try:
            as_set = as_set.split("::")[1]
        except IndexError:
            pass

    except KeyError:
        as_set = None


    return (name, as_set)


# Begin HTML handlers

def get_member_html(network_id, member_id):
    member = controller.get_member(network_id, member_id)
    asn = 34553

    asn_name_set = get_asn_name_set(asn)

    member_ip = "None"
    try:
        member_ip = member["ipAssignments"][0]
    except IndexError:
        pass

    if member["authorized"]:
        authorized = "<a style='color: green;' href='/member/toggle?id=" + member["id"] + "'>Authorized</a>"
    else:
        authorized = "<a style='color: red;' href='/member/toggle?id=" + member["id"] + "'>Unauthorized</a>"

    return """<tr>
                <td><a href='https://bgp.he.net/AS""" + str(asn) + """'>""" + str(asn) + """</a></td>
                <td><a href='https://peeringdb.com/net?asn=""" + str(asn) + """'>""" + asn_name_set[0] + """</a></td>
                <td>""" + asn_name_set[1] + """</td>
                <td>""" + member["id"] + """</td>
                <td ondblclick="addressChangePrompt('""" + member["id"] + """', '""" + member_ip + """')"><b>""" + member_ip + """</b></td>
                <td>""" + str(member["vMajor"]) + """.""" + str(member["vMinor"]) + """.""" + str(member["vRev"]) + """</td>
                <td>""" + authorized + """</td>
              </tr>"""


def get_members_html(network_id):
    html = ""
    for member in controller.get_members(network_id):
        html += get_member_html(network_id, member)
    return html

def get_routes_html(network_id):
    html = ""

    for route in controller.get_routes(network_id):
        html += """<tr>
                    <td>""" + route + """</td>
                   </tr>"""

    return html
