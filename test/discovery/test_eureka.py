import unittest
import mock
from ballast.compat import unicode
from requests import models
from ballast.discovery.eureka import EurekaRestRecordList
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


# string encoding not completely compatible
# between python 2-3...
def str_compat(s, encoding):
    try:
        return unicode(s, encoding)
    except TypeError:
        return unicode(s).encode(encoding)


_MOCK_RESPONSE = str_compat("""
{
    "application": {
        "name": "MY-APP",
        "instance": [
            {
                "hostName": "my-service-host.local",
                "app": "my-service",
                "ipAddr": "10.0.0.13",
                "status": "UP",
                "overriddenstatus": "UNKNOWN",
                "port": {
                    "$": 8083,
                    "@enabled": "true"
                },
                "securePort": {
                    "$": 8443,
                    "@enabled": "true"
                },
                "countryId": 1,
                "dataCenterInfo": {
                    "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                    "name": "MyOwn"
                },
                "leaseInfo": {
                    "renewalIntervalInSecs": 30,
                    "durationInSecs": 90,
                    "registrationTimestamp": 1503094118627,
                    "lastRenewalTimestamp": 1503094118627,
                    "evictionTimestamp": 0,
                    "serviceUpTimestamp": 0
                },
                "metadata": {
                    "@class": "java.util.Collections$EmptyMap"
                },
                "homePageUrl": "http://WKS-SOF-L012:8083",
                "statusPageUrl": "http://WKS-SOF-L012:8083/status",
                "healthCheckUrl": "http://WKS-SOF-L012:8083/healthcheck",
                "vipAddress": "com.automationrhapsody.eureka.app",
                "secureVipAddress": "com.automationrhapsody.eureka.app",
                "isCoordinatingDiscoveryServer": "false",
                "lastUpdatedTimestamp": "1503094118627",
                "lastDirtyTimestamp": "1503094118112",
                "actionType": "ADDED"
            }
        ]
    }
}
""", 'utf-8')


_MOCK_SSL_ONLY_RESPONSE = str_compat("""
{
    "application": {
        "name": "MY-APP",
        "instance": [
            {
                "hostName": "my-service-host.local",
                "app": "my-service",
                "ipAddr": "10.0.0.13",
                "status": "UP",
                "overriddenstatus": "UNKNOWN",
                "port": {
                    "$": 8083,
                    "@enabled": "false"
                },
                "securePort": {
                    "$": 8443,
                    "@enabled": "true"
                },
                "countryId": 1,
                "dataCenterInfo": {
                    "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                    "name": "MyOwn"
                },
                "leaseInfo": {
                    "renewalIntervalInSecs": 30,
                    "durationInSecs": 90,
                    "registrationTimestamp": 1503094118627,
                    "lastRenewalTimestamp": 1503094118627,
                    "evictionTimestamp": 0,
                    "serviceUpTimestamp": 0
                },
                "metadata": {
                    "@class": "java.util.Collections$EmptyMap"
                },
                "homePageUrl": "http://WKS-SOF-L012:8083",
                "statusPageUrl": "http://WKS-SOF-L012:8083/status",
                "healthCheckUrl": "http://WKS-SOF-L012:8083/healthcheck",
                "vipAddress": "com.automationrhapsody.eureka.app",
                "secureVipAddress": "com.automationrhapsody.eureka.app",
                "isCoordinatingDiscoveryServer": "false",
                "lastUpdatedTimestamp": "1503094118627",
                "lastDirtyTimestamp": "1503094118112",
                "actionType": "ADDED"
            }
        ]
    }
}
""", 'utf-8')


_MOCK_NON_SSL_ONLY_RESPONSE = str_compat("""
{
    "application": {
        "name": "MY-APP",
        "instance": [
            {
                "hostName": "my-service-host.local",
                "app": "my-service",
                "ipAddr": "10.0.0.13",
                "status": "UP",
                "overriddenstatus": "UNKNOWN",
                "port": {
                    "$": 8083,
                    "@enabled": "true"
                },
                "securePort": {
                    "$": 8443,
                    "@enabled": "false"
                },
                "countryId": 1,
                "dataCenterInfo": {
                    "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                    "name": "MyOwn"
                },
                "leaseInfo": {
                    "renewalIntervalInSecs": 30,
                    "durationInSecs": 90,
                    "registrationTimestamp": 1503094118627,
                    "lastRenewalTimestamp": 1503094118627,
                    "evictionTimestamp": 0,
                    "serviceUpTimestamp": 0
                },
                "metadata": {
                    "@class": "java.util.Collections$EmptyMap"
                },
                "homePageUrl": "http://WKS-SOF-L012:8083",
                "statusPageUrl": "http://WKS-SOF-L012:8083/status",
                "healthCheckUrl": "http://WKS-SOF-L012:8083/healthcheck",
                "vipAddress": "com.automationrhapsody.eureka.app",
                "secureVipAddress": "com.automationrhapsody.eureka.app",
                "isCoordinatingDiscoveryServer": "false",
                "lastUpdatedTimestamp": "1503094118627",
                "lastDirtyTimestamp": "1503094118112",
                "actionType": "ADDED"
            }
        ]
    }
}
""", 'utf-8')


class _MockResponse(models.Response):

    def __init__(self, content, status_code=200):
        super(_MockResponse, self).__init__()
        self._content = content
        self.status_code = status_code


class EurekaRestRecordListTest(unittest.TestCase):

    @mock.patch('ballast.discovery.eureka.requests.get', return_value=_MockResponse(_MOCK_RESPONSE))
    def test_resolve(self, mock_get_request):

        eureka_base_url = 'http://my.eureka.url'
        service = 'my-service'

        servers = EurekaRestRecordList(eureka_base_url, service, False)

        # resolve some servers
        server_list = list(servers.get_servers())
        self.assertEqual(1, len(server_list))
        self.assertEqual('my-service-host.local', server_list[0].address)
        self.assertEqual(8083, server_list[0].port)
        self.assertEqual(30, server_list[0].ttl)

        # verify request url was properly formatted
        args = mock_get_request.call_args[0]
        actual_url = urlparse(args[0])

        self.assertEqual(actual_url.scheme, 'http')
        self.assertEqual(actual_url.hostname, 'my.eureka.url')
        self.assertEqual(actual_url.path, '/eureka/v2/apps/my-service')

    @mock.patch('ballast.discovery.eureka.requests.get', return_value=_MockResponse(_MOCK_SSL_ONLY_RESPONSE))
    def test_resolve_ssl_only(self, mock_get_request):

        eureka_base_url = 'http://my.eureka.url'
        service = 'my-service'

        # create Eureka server list favoring non-secure port
        servers = EurekaRestRecordList(eureka_base_url, service, False)

        # resolve some servers
        server_list = list(servers.get_servers())
        self.assertEqual(1, len(server_list))
        self.assertEqual('my-service-host.local', server_list[0].address)
        self.assertEqual(8443, server_list[0].port)
        self.assertEqual(30, server_list[0].ttl)

        # verify request url was properly formatted
        args = mock_get_request.call_args[0]
        actual_url = urlparse(args[0])

        self.assertEqual(actual_url.scheme, 'http')
        self.assertEqual(actual_url.hostname, 'my.eureka.url')
        self.assertEqual(actual_url.path, '/eureka/v2/apps/my-service')

    @mock.patch('ballast.discovery.eureka.requests.get', return_value=_MockResponse(_MOCK_NON_SSL_ONLY_RESPONSE))
    def test_resolve_non_ssl_only(self, mock_get_request):

        eureka_base_url = 'http://my.eureka.url'
        service = 'my-service'

        # create Eureka server list favoring secure port
        servers = EurekaRestRecordList(eureka_base_url, service, True)

        # resolve some servers
        server_list = list(servers.get_servers())
        self.assertEqual(1, len(server_list))
        self.assertEqual('my-service-host.local', server_list[0].address)
        self.assertEqual(8083, server_list[0].port)
        self.assertEqual(30, server_list[0].ttl)

        # verify request url was properly formatted
        args = mock_get_request.call_args[0]
        actual_url = urlparse(args[0])

        self.assertEqual(actual_url.scheme, 'http')
        self.assertEqual(actual_url.hostname, 'my.eureka.url')
        self.assertEqual(actual_url.path, '/eureka/v2/apps/my-service')

    @mock.patch('ballast.discovery.eureka.requests.get', return_value=_MockResponse('', 404))
    def test_resolve_no_services(self, mock_get_request):

        eureka_base_url = 'http://my.eureka.url'
        service = 'my-service'

        servers = EurekaRestRecordList(eureka_base_url, service, False)

        # resolve some servers
        server_list = list(servers.get_servers())
        self.assertEqual(0, len(server_list))

    @mock.patch('ballast.discovery.eureka.requests.get', return_value=_MockResponse(_MOCK_RESPONSE))
    def test_resolve_with_secure_port(self, mock_get_request):

        eureka_base_url = 'http://my.eureka.url'
        service = 'my-service'

        servers = EurekaRestRecordList(eureka_base_url, service)

        # resolve some servers
        server_list = list(servers.get_servers())
        self.assertEqual(1, len(server_list))
        self.assertEqual('my-service-host.local', server_list[0].address)
        self.assertEqual(8443, server_list[0].port)
        self.assertEqual(30, server_list[0].ttl)

        # verify request url was properly formatted
        args = mock_get_request.call_args[0]
        actual_url = urlparse(args[0])

        self.assertEqual(actual_url.scheme, 'http')
        self.assertEqual(actual_url.hostname, 'my.eureka.url')
        self.assertEqual(actual_url.path, '/eureka/v2/apps/my-service')
