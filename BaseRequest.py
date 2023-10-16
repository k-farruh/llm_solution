# -*- coding: utf-8 -*-

import time
from typing import Dict, Any

from Tea.core import TeaCore
from Tea.exceptions import TeaException, UnretryableException
from Tea.model import TeaModel
from Tea.request import TeaRequest
from alibabacloud_credentials import models as credential_models
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_opensearch_util.opensearch_util import OpensearchUtil
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class Config(TeaModel):
    """
 Config
 用于配置环境相关参数信息.
 """
    def __init__(
            self,
            endpoint: str = None,
            protocol: str = None,
            type: str = None,
            security_token: str = None,
            access_key_id: str = None,
            access_key_secret: str = None,
            user_agent: str = "",
    ):
        self.endpoint = endpoint
        self.protocol = protocol
        self.type = type
        self.security_token = security_token
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.user_agent = user_agent


class Client:
    """
    OpensearchClient
    用于 opensearch Client 请求 参数组装及发送请求.
    """
    _endpoint: str = None
    _protocol: str = None
    _user_agent: str = None
    _credential: CredentialClient = None

    def __init__(
            self,
            config: Config,
    ):
        if UtilClient.is_unset(config):
            raise TeaException({
                'name': 'ParameterMissing',
                'message': "'config' can not be unset"
            })
        if UtilClient.empty(config.type):
            config.type = 'access_key'
        credential_config = credential_models.Config(
            access_key_id=config.access_key_id,
            type=config.type,
            access_key_secret=config.access_key_secret,
            security_token=config.security_token
        )
        self._credential = CredentialClient(credential_config)
        self._endpoint = config.endpoint
        self._protocol = config.protocol
        self._user_agent = config.user_agent

    def _request(
            self,
            method: str,
            pathname: str,
            query: Dict[str, Any],
            headers: Dict[str, str],
            body: Any,
            runtime: util_models.RuntimeOptions,
    ) -> Dict[str, Any]:
        """
        执行 TeaRequest .
        :param request: TeaRequest
        :param runtime: util_models.RuntimeOptions
        :return: Dict[str, Any]
        """
        runtime.validate()
        _runtime = {
            'timeouted': 'retry',
            'readTimeout': runtime.read_timeout,
            'connectTimeout': runtime.connect_timeout,
            'httpProxy': runtime.http_proxy,
            'httpsProxy': runtime.https_proxy,
            'noProxy': runtime.no_proxy,
            'maxIdleConns': runtime.max_idle_conns,
            'retry': {
                'retryable': runtime.autoretry,
                'maxAttempts': UtilClient.default_number(runtime.max_attempts, 3)
            },
            'backoff': {
                'policy': UtilClient.default_string(runtime.backoff_policy, 'no'),
                'period': UtilClient.default_number(runtime.backoff_period, 1)
            },
            'ignoreSSL': runtime.ignore_ssl
        }
        _last_request = None
        _last_exception = None
        _now = time.time()
        _retry_times = 0
        while TeaCore.allow_retry(_runtime.get('retry'), _retry_times, _now):
            if _retry_times > 0:
                _backoff_time = TeaCore.get_backoff_time(_runtime.get('backoff'), _retry_times)
                if _backoff_time > 0:
                    TeaCore.sleep(_backoff_time)
            _retry_times = _retry_times + 1
            try:
                _request = TeaRequest()
                accesskey_id = self._credential.get_access_key_id()
                access_key_secret = self._credential.get_access_key_secret()
                security_token = self._credential.get_security_token()
                _request.protocol = UtilClient.default_string(self._protocol, 'HTTP')
                _request.method = method
                _request.pathname = pathname
                _request.headers = TeaCore.merge({
                    'user-agent': UtilClient.get_user_agent(self._user_agent),
                    'Content-Type': 'application/json',
                    'Date': OpensearchUtil.get_date(),
                    'host': UtilClient.default_string(self._endpoint, f'opensearch-cn-hangzhou.aliyuncs.com'),
                    'X-Opensearch-Nonce': UtilClient.get_nonce()
                }, headers)
                if not UtilClient.is_unset(query):
                    _request.query = UtilClient.stringify_map_value(query)
                if not UtilClient.is_unset(body):
                    req_body = UtilClient.to_jsonstring(body)
                    _request.headers['Content-MD5'] = OpensearchUtil.get_content_md5(req_body)
                    _request.body = req_body
                if not UtilClient.is_unset(security_token):
                    _request.headers["X-Opensearch-Security-Token"] = security_token
                _request.headers['Authorization'] = OpensearchUtil.get_signature(_request, accesskey_id,
                                                                                 access_key_secret)
                _last_request = _request
                _response = TeaCore.do_action(_request, _runtime)
                obj_str = UtilClient.read_as_string(_response.body)
                if UtilClient.is_4xx(_response.status_code) or UtilClient.is_5xx(_response.status_code):
                    raise TeaException({
                        'message': _response.status_message,
                        'data': obj_str,
                        'code': _response.status_code
                    })
                obj = UtilClient.parse_json(obj_str)
                res = UtilClient.assert_as_map(obj)
                return {
                    'body': res,
                    'headers': _response.headers
                }
            except TeaException as e:
                if TeaCore.is_retryable(e):
                    _last_exception = e
                    continue
                raise e
        raise UnretryableException(_last_request, _last_exception)
        