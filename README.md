# lil_bind Ansible Galaxy Collection 
  

---
lil_bind installs  Bind9 podman container and configures a ***static DNS*** for you

---
- one domain and ip per zone
- subdomains can be used, or just left blank
  
i dont need a dhcp for my iac stuff, but still need a dns, so it was not intendet to make use of dynamic updates since all my containers and vms have a static ip because of the nic's (bridges/nats) anyway, so i decided just to use a tailscale router and instead of dhcp ill use a little netkwork manager that gives ip by the given zone. So i just have a preset file that contains all my zones and subnets and the networkmanager will cycle ips in the given subnet and zone.

## Install
```bash
$ ansible-galaxy collection install ji_podhead.lil_bind
```
---

## Usage
- import collection and use root
      
    ```yaml
    
    - hosts: <your_host>
      gather_facts: no
      become: true
      become_method: sudo
      become_user: root
      collections:
        - ji_podhead.lil_bind 
    ```
    
- put all variables in a block because some are needed  for multiple roles and we dont like redundancy
  
    ```yaml
  tasks:
    - name: install podman
      ansible.builtin.yum:
        name:
        - podman
        state: latest
    - name: lil_bind
      vars:
          container_name: "dns"
          container_ip: "192.168.22.2"        
          dns_admin: "admin"
          dns_domain: "dns.com"
          bridge_name: "my_bridge"
          bridge_ip_range: "192.168.22.128/25"
          bridge_subnet: "192.168.22.0/24"
          bridge_gateway: "192.168.22.1"
          domains: [
                      {
                        domain: "pod.com", ip: "192.168.3.0",
                        sub_domains: [{sub_domain: "tele", ip: 2}]
                      },
                      {
                        domain: "test.com", ip: "192.168.2.120",
                        sub_domains: [{sub_domain: "test", ip: "121"}]
                      }
                    ]        
          forwarders: [100.100.100.100]
          subnets: [192.168.0.0/16,100.0.0.0/8]
          allow_queries: ["localhost","192.168.0.0/16","100.0.0.0/8"]
      
    ```
    
- fire the collection
    ```yaml      
      block:
      - name: create bridge
        import_role:
          name: ji_podhead.lil_bind.create_bridge

      - name: install bind9
        import_role: 
          name: ji_podhead.lil_bind.install

      - name: config
        import_role: 
          name: ji_podhead.lil_bind.config

      - name: set_zones
        import_role: 
          name: ji_podhead.lil_bind.set_zones
      
      - name: update & restart bind9
        import_role:
          name: ji_podhead.lil_bind.update
    ```
    
    --- 

## output
```bash
######################################################
#           /etc/bind/named.conf.local
######################################################
//
// Do any local configuration here
//

// Consider adding the 1918 zones here, if they are not used in your
// organization
//include "/etc/bind/zones.rfc1918";

zone "pod.com" IN {  
      type master;     
      file "/etc/bind/zones/pod.com";    
      allow-query { any; };   
      allow-update { any; };  
};      
zone "3.168.192.in-addr.arpa" IN {       
      type master;     
      file "/etc/bind/zones/pod.com.rev";     
      allow-query { any; };   
      allow-update { any; };  
};      
zone "test.com" IN {  
      type master;     
      file "/etc/bind/zones/test.com";    
      allow-query { any; };   
      allow-update { any; };  
};      
zone "2.168.192.in-addr.arpa" IN {       
      type master;     
      file "/etc/bind/zones/test.com.rev";     
      allow-query { any; };   
      allow-update { any; };  
};

######################################################
#           /etc/bind/named.conf.options
######################################################
acl local-lan { 
    localhost;
    192.168.0.0/16;
    100.0.0.0/8;
    };
options {
    directory "/var/cache/bind";
    forwarders {
      100.100.100.100;
          };
    allow-query { 
    localhost;
    192.168.0.0/16;
    100.0.0.0/8;
        };
    dnssec-validation auto;
    auth-nxdomain no;    // conform to RFC1035
    listen-on-v6 { any; };
    recursion no;  // we set that to no to avoid unnecessary traffic
    querylog yes; // Enable for debugging
    version "not available"; // Disable for security
};
 
######################################################
#             /etc/bind/zones/pod.com
######################################################
;
; BIND data file for local loopback interface
;
$TTL    604800
@       IN      SOA     dns.com. admin. ( 
                                        2    
                                        604800     
                                        86400   
                                        2419200    
                                        604800 )      
;
@       IN      NS      dns.com.
pod.com. IN  A  192.168.3.0
tele.pod.com. IN  A  192.168.3.2

######################################################
#           /etc/bind/zones/pod.com.rev
######################################################
;
; BIND reverse data file for local loopback interface
;
$TTL    604800
@       IN      SOA     dns.com. admin. ( 
                                        2    
                                        604800     
                                        86400   
                                        2419200    
                                        604800 )      
;
@       IN      NS     dns.com.
0 IN  PTR  pod.com.
2    IN  PTR tele.pod.com.

######################################################
#                /etc/bind/zones/test.com
######################################################
;
; BIND data file for local loopback interface
;
$TTL    604800
@       IN      SOA     dns.com. admin. ( 
                                        2    
                                        604800     
                                        86400   
                                        2419200    
                                        604800 )      
;
@       IN      NS      dns.com.
test.com. IN  A  192.168.2.120
test.test.com. IN  A  192.168.2.121

######################################################
#             /etc/bind/zones/test.com.rev
######################################################
;
; BIND reverse data file for local loopback interface
;
$TTL    604800
@       IN      SOA     dns.com. admin. ( 
                                        2    
                                        604800     
                                        86400   
                                        2419200    
                                        604800 )      
;
@       IN      NS     dns.com.
120 IN  PTR  test.com.
121    IN  PTR test.test.com.
```
