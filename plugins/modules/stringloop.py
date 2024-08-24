#!/usr/bin/env python3
# ji_podhead/host_prototypes/utils/generate_mac_adress.py

DOCUMENTATION = '''
---
module: generate_mac_adress
short_description: Generiert eine MAC-Adresse
description:
    - Generiert eine zufällige MAC-Adresse
options:
    - name:
        description:
            - Der Name der MAC-Adresse
        required: true
        type: str
author:
    - Ihr Name
'''


import os
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.facts import ansible_facts, get_all_facts
import tempfile
import re
#from hvac import Client as hvac_client
#from ..module_utils.hvac import Client as hvac_client
import urllib.request
import urllib.parse
import json


                  

class AnsiblePrint:
    def __init__(self, module):
        self.status = {"log":[], "return":None}
        self.module = module

    def log(self, string):
        string = str(string)
        self.status["log"].append(string)
        self.module.log(string)
        # self.module.info(string)

    def fail(self, msg, err):
        self.status["return"] = {"type": "Error", "value": err}
        to_native(self.status)
        self.module.fail_json(msg=msg)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            string=dict(default=''),
            replacements=dict(required=True),  # {replacements:{pre:"some sintr to put before replacement", post:"some string to put after replacement"}}

        ),
    )
    ansiblePrint = AnsiblePrint(module=module)
    string = module.params['string']
    replacements = module.params['replacements'] 

    try:
        with tempfile.TemporaryFile(mode='w+t') as tmp:
            replacements=(replacements[0] + "{" + replacements[1:-2] + "}" + replacements[-1]).replace("\\\"  \\\"","\\\",  \\\"")
            replacements = json.loads(replacements)
            tmp.write(replacements)
            tmp.seek(0)
            replacements = json.load(tmp)
            newstring=""
            for key,val in replacements.items():
                #if(targets[0] is "all" or targets.__contains__(key) ):
                                    # Setze den Vault-Token
                    ansiblePrint.log("--------------")
                    ansiblePrint.log("adding to secrets: key= " + key + " value= " + val)
                    secrets[key]=val
                    ansiblePrint.log(antwort)


            ansiblePrint.log(newstring)

        secrets={}
        ansiblePrint.status["return"]=secrets

    except Exception as e:
        ansiblePrint.fail(e,"error",) 
    module.exit_json(result=ansiblePrint.status)
    module._log_to_syslog


if __name__ == "__main__":
    main()