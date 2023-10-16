# -*- coding: utf-8 -*-
import time, os
from typing import Dict, Any

from Tea.exceptions import TeaException
from Tea.request import TeaRequest
from alibabacloud_tea_util import models as util_models
from BaseRequest import Config, Client
from BaseRequest import Config, Client

from dotenv import load_dotenv


class LLMSearch:
    def __init__(self, config: Config):
        self.Clients = Client(config=config)
        self.runtime = util_models.RuntimeOptions(
            connect_timeout=10000,
            read_timeout=10000,
            autoretry=False,
            ignore_ssl=False,
            max_idle_conns=50,
            max_attempts=3
        )
        self.header = {}


    def searchDoc(self, app_name: str,body:Dict, query_params: dict={}) -> Dict[str, Any]:
        try:
            response = self.Clients._request(method="POST", pathname=f'/v3/openapi/apps/{app_name}/actions/knowledge-search',
                                             query=query_params, headers=self.header, body=body, runtime=self.runtime)
            return response
        except TeaException as e:
            print(e)


def opensearch_query(prompt, filter):
    # Load environment variables from .env file in the current directory
    load_dotenv()

    # Specify the endpoint of the OpenSearch API. The value does not contain the http:// prefix.
    endpoint = "opensearch-ap-southeast-1.aliyuncs.com"

    # Specify the request protocol. Valid values: HTTPS and HTTP.
    endpoint_protocol = "HTTP"

    # Specify your AccessKey pair.
    # Obtain the AccessKey ID and AccessKey secret from environment variables. 
    # You must configure environment variables before you run this code. For more information, see the "Configure environment variables" section of this topic.
    access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
    access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

    # Specify the authentication method. Default value: access_key. A value of sts indicates authentication based on Resource Access Management (RAM) and Security Token Service (STS).
    # Valid values: sts and access_key.
    auth_type = "access_key"

    # If you use authentication based on RAM and STS, you must specify the security_token parameter. You can call the AssumeRole operation of Alibaba Cloud RAM to obtain an STS token.
    # security_token =  "<security_token>"

    # Specify common request parameters.
    # The type and security_token parameters are required only if you use the SDK as a RAM user.
    Configs = Config(endpoint=endpoint, access_key_id=access_key_id, access_key_secret=access_key_secret,
                      type=auth_type, protocol=endpoint_protocol)

    # Create an OpenSearch instance.
    ops = LLMSearch(Configs)
    app_name = "nbd_test"

    # --------------- Search for documents ---------------

    docQuery = {
            "question": {"text": prompt, "type": "TEXT"},
            "options": {
                "chat": {
                    "prompt_config": {
                        "language": "English"
                    }
                },
                "retrieve": {
                    "doc": {
                        "filter": f"category=\"{filter}\""
                    }
                }
            }
    }
    print(prompt, filter)
    res1 = ops.searchDoc(app_name=app_name, body=docQuery)
    return res1
    print("\nReference document: ", res1["body"]["result"]["data"][0]["reference"][0]["title"])
    print("\nAnswer: ", res1["body"]["result"]["data"][0]["answer"])
    print('Anything else?')

opensearch_query("tell me about enbd credit card", "Alshaya Group")

# tell me about enbd credit card