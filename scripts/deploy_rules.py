"""Ανεβάζει το firestore.rules στο Firebase (τρέχει στο GitHub Actions με το FIREBASE_SA)."""
import json, os, sys
import requests
from google.oauth2 import service_account
import google.auth.transport.requests as gr

sa = json.loads(os.environ["FIREBASE_SA"]); pid = sa["project_id"]
cr = service_account.Credentials.from_service_account_info(sa, scopes=["https://www.googleapis.com/auth/cloud-platform"])
cr.refresh(gr.Request()); H = {"Authorization": "Bearer " + cr.token}
src = open("firestore.rules", encoding="utf-8").read()
base = "https://firebaserules.googleapis.com/v1/projects/%s" % pid
r = requests.post(base + "/rulesets", headers=H, json={"source": {"files": [{"name": "firestore.rules", "content": src}]}}, timeout=30)
print("ruleset", r.status_code); r.raise_for_status()
name = r.json()["name"]
r = requests.patch(base + "/releases/cloud.firestore", headers=H, json={"release": {"name": "projects/%s/releases/cloud.firestore" % pid, "rulesetName": name}}, timeout=30)
print("release", r.status_code, r.text[:200]); r.raise_for_status()
print("οι κανόνες ενημερώθηκαν:", name)
