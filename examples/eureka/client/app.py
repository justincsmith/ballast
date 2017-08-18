import ballast
from ballast.discovery.eureka import EurekaRestRecordList

# create an Eureka server list pointing to our Eureka server
server_list = EurekaRestRecordList('http://localhost:8080', 'my-service', False)
load_balancer = ballast.LoadBalancer(server_list)
service = ballast.Service(load_balancer)

print("Hello world! " + service.get('/'))
