# server.py PKIX main server file
#
# Author: Nate Sales
#
# This file provides all flask webserver functionality besides html templating

from flask import Flask, render_template, Markup, request, redirect

import pkix
import zerotier

import time

app = Flask(__name__)
controller = zerotier.Controller()
pkix.controller = controller

with open("nwid.txt", "r") as nwid_file:
    _NWID = nwid_file.read().strip()

@app.route("/")
def index():
    return render_template("index.html",
                           network_id=_NWID,

                           username="admin",

                           total_members=len(controller.get_members(_NWID)),
                           routes_length=len(controller.get_routes(_NWID)),


                           member_html=Markup(pkix.get_members_html(_NWID)),
                           routes = Markup(pkix.get_routes_html(_NWID)),
                           controller_version=controller.status()["version"],
                           controller_clock=controller.status()["clock"]
                           )


@app.route("/member/toggle")
def member_toggle():
    _id = request.args.get("id")

    controller.toggle_member_authorization(_NWID, _id)

    return redirect("/")


@app.route("/member/ip")
def member_id():
    _id = request.args.get("id")
    ip = request.args.get("ip")

    controller.set_member_ip(_NWID, _id, ip)

    return redirect("/")


@app.route("/network/route")
def network_route():
    route = request.args.get("route")

    controller.add_route(_NWID, route)

    return redirect("/")


@app.route("/network/zero")
def network_zero():
    controller.set_routes(_NWID, [])

    return redirect("/")

app.run("localhost", port=80, debug=True)
