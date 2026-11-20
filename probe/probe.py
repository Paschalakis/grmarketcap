import json, os, urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests as gr
sa=json.loads(os.environ["FIREBASE_SA"]); pid=sa["project_id"]
cr=service_account.Credentials.from_service_account_info(sa,scopes=["https://www.googleapis.com/auth/cloud-platform","https://www.googleapis.com/auth/firebase"])
cr.refresh(gr.Request()); H={"Authorization":"Bearer "+cr.token}
def get(u):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
    except Exception as e: return {"ERR":str(e)}
rel=get("https://firebaserules.googleapis.com/v1/projects/%s/releases/cloud.firestore"%pid)
print("release", rel.get("rulesetName"), rel.get("ERR"))
if rel.get("rulesetName"):
    rs=get("https://firebaserules.googleapis.com/v1/"+rel["rulesetName"])
    for f in rs.get("source",{}).get("files",[]): print("----",f.get("name")); print(f.get("content"))
# τεστ δικαιώματος
req=urllib.request.Request("https://cloudresourcemanager.googleapis.com/v1/projects/%s:testIamPermissions"%pid,data=json.dumps({"permissions":["firebaserules.rulesets.create","firebaserules.releases.update","datastore.entities.update"]}).encode(),headers={**H,"Content-Type":"application/json"})
try: print("perms",json.load(urllib.request.urlopen(req,timeout=30)))
except Exception as e: print("perms ERR",e)
import firebase_admin
from firebase_admin import auth, credentials
firebase_admin.initialize_app(credentials.Certificate(sa))
try: print("owner uid", auth.get_user_by_email(os.environ["GMAIL_USER"]).uid)
except Exception as e: print("owner ERR", type(e).__name__)
