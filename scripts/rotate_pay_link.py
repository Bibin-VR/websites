#!/usr/bin/env python3
"""Keep exactly one unpaid ₹3,999 Razorpay Payment Link published on the site.

A Razorpay Payment Link can only be paid once, so after every sale this script
creates a fresh link and writes it into assets/config.js (payUrl + payLinkId).

Keys come from RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET in the environment
(GitHub Actions secrets) or, when run locally, from ../.env next to this repo.
Never prints secrets or customer data: only link IDs, statuses and the public URL.
"""
import base64
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "assets" / "config.js"
API = "https://api.razorpay.com/v1"
SITE = "https://bibin-vr.github.io/websites/"
AMOUNT_PAISE = 399900  # ₹3,999


def load_keys():
    kid = os.environ.get("RAZORPAY_KEY_ID", "").strip()
    sec = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()
    env = ROOT.parent / ".env"
    if not (kid and sec) and env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k == "RAZORPAY_KEY_ID" and not kid:
                    kid = v
                elif k == "RAZORPAY_KEY_SECRET" and not sec:
                    sec = v
    if not (kid and sec):
        sys.exit("Razorpay keys not found (RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET).")
    return kid, sec


def call(method, path, keys, body=None):
    auth = base64.b64encode(f"{keys[0]}:{keys[1]}".encode()).decode()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path, data=data, method=method,
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read() or b"{}")
        except Exception:
            payload = {}
        return e.code, payload


def err(res):
    return (res.get("error") or {}).get("description", "")


def read_config():
    txt = CONFIG.read_text()
    m = re.search(r'payLinkId:\s*"([^"]*)"', txt)
    return txt, (m.group(1) if m else "")


def write_config(txt, url, link_id):
    txt = re.sub(r'payUrl:\s*"[^"]*"', f'payUrl: "{url}"', txt, count=1)
    if re.search(r'payLinkId:\s*"[^"]*"', txt):
        txt = re.sub(r'payLinkId:\s*"[^"]*"', f'payLinkId: "{link_id}"', txt, count=1)
    else:
        txt = txt.replace(f'payUrl: "{url}",', f'payUrl: "{url}",\n  payLinkId: "{link_id}",', 1)
    CONFIG.write_text(txt)


def create_link(keys):
    body = {
        "amount": AMOUNT_PAISE,
        "currency": "INR",
        "accept_partial": False,
        "description": "Business website, live in 24 hours. One-page site, hosting included, 2 rounds of changes.",
        "reference_id": f"web24-{int(time.time())}",
        "notes": {"product": "website-24h", "source": SITE},
        "callback_url": SITE + "thanks.html",
        "callback_method": "get",
        "reminder_enable": False,
        "options": {"checkout": {"name": "Bibin V R · Websites in 24 hours"}},
    }
    st, res = call("POST", "/payment_links", keys, body)
    if st >= 400:
        print(f"create with custom checkout name failed (HTTP {st}: {err(res)}); retrying without it")
        body.pop("options")
        st, res = call("POST", "/payment_links", keys, body)
    if st >= 400:
        sys.exit(f"Could not create payment link: HTTP {st} {err(res)}")
    return res["id"], res["short_url"]


def main():
    keys = load_keys()
    mode = "live" if keys[0].startswith("rzp_live_") else "test" if keys[0].startswith("rzp_test_") else "unknown"
    txt, link_id = read_config()
    if link_id:
        st, res = call("GET", f"/payment_links/{link_id}", keys)
        status = res.get("status") if st < 400 else f"http-{st}"
        print(f"mode={mode} current={link_id} status={status}")
        if status == "created":
            return  # still unpaid: nothing to do
    else:
        print(f"mode={mode} no link published yet")
    new_id, url = create_link(keys)
    write_config(txt, url, new_id)
    print(f"published {new_id} -> {url}")


if __name__ == "__main__":
    main()
