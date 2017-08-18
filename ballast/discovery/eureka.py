import logging
import requests
from ballast.compat import unicode
from ballast.util import UrlBuilder
from ballast.discovery import Server, ServerList


class EurekaRestRecordList(ServerList):

    _SERVICE_URL = '/eureka/v2/apps/'

    def __init__(self, base_url, service, use_secure_port=True):
        super(EurekaRestRecordList, self).__init__()
        self.base_url = base_url
        self.service = service
        self.use_secure_port = use_secure_port
        self._logger = logging.getLogger(self.__module__)

    def get_servers(self):

        try:
            url = UrlBuilder.from_url(self.base_url)
            url.path(self._SERVICE_URL)
            url.append_path(self.service)

            headers = {'accept': 'application/json'}
            response = requests.get(unicode(url), headers=headers)
            if not response.ok:
                raise StopIteration()

            json = response.json()
            application = json['application']

            for instance in application['instance']:
                port = EurekaRestRecordList._get_port(instance, self.use_secure_port)
                s = Server(
                    instance['hostName'],
                    port,
                    ttl=instance['leaseInfo']['renewalIntervalInSecs']
                )

                # if instance is UP, lets set this server to alive
                s._is_alive = str(instance['status']).upper() == 'UP'

                self._logger.debug("Created server from Eureka REST API record: %s", s)

                yield s

        except:
            return

    @staticmethod
    def _get_port(instance, use_secure):

        # favor the secure port if this is true and the secure port is enabled
        if use_secure:
            if instance['securePort']['@enabled'] == 'true':
                return instance['securePort']['$']
            else:
                return instance['port']['$']

        if instance['port']['@enabled'] == 'true':
            return instance['port']['$']
        else:
            return instance['securePort']['$']
