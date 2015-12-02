'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment 2
Professor: Nick Feamster
Teaching Assistant: Arpit Gupta, Muhammad Shahbaz
'''

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.link import TCLink
import pdb

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1=None, linkopts2=None, linkopts3=None,
                 fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        # Add your logic here ...
        # create tree of network elements
        tree = {}
        ipid = 1
        for level in ('c', 'a', 'e', 'h'):
            if level == 'c':
                tree['c'] = {'node':self.addSwitch(level, dpid=int2dpid(ipid)),'children':{} }
                ipid += 1
            elif level == 'a':
                for child_no in range(fanout):
                    key = '{}{}'.format(level, child_no)
                    sw = self.addSwitch(key, dpid=int2dpid(ipid))
                    ipid += 1
                    tree['c']['children'][key]={'node':sw, 'children':{}}
                    sw_c = tree['c']['node']
                    self.addLink(sw_c, sw, **linkopts1)
            elif level == 'e':
                for a_key in tree['c']['children']:
                    key_prfx = '{}{}'.format(level, a_key[1:])
                    for child_no in range(fanout):
                        e_key = '{}{}'.format(key_prfx, child_no) 
                        sw = self.addSwitch(e_key, dpid=int2dpid(ipid))
                        ipid += 1
                        tree['c']['children'][a_key]['children'][e_key]={'node':sw, 'children':{}}
                        sw_a = tree['c']['children'][a_key]['node']
                        self.addLink(sw_a, sw, **linkopts2)
            elif level == 'h':
                for a_key in tree['c']['children']:
                    for e_key in tree['c']['children'][a_key]['children']:
                        key_prfx = '{}{}'.format(level, e_key[1:])
                        for child_no in range(fanout):
                            h_key = '{}{}'.format(key_prfx, child_no)
                            host = self.addHost(h_key, dpid=int2dpid(ipid))
                            ipid += 1
                            tree['c']['children'][a_key]['children'][e_key]['children'][h_key] = {'node':host}
                            sw = tree['c']['children'][a_key]['children'][e_key]['node']
                            self.addLink(host, sw, **linkopts3)

def int2dpid(dpid):
    try:
        dpid = hex( dpid )[ 2: ]
        dpid = '0' * ( 16 - len( dpid ) ) + dpid
        return dpid
    except IndexError:
        raise Exception('Unable to derive default datapath ID - '
                        'please either specify a dpid or use a '
                        'canonical switch name such as s23.') 

topos = { 'custom': ( lambda: CustomTopo() ) }

def myTest():
    l1 = {'bw':50, 'delay':'5ms'}
    l2 = {'bw':30, 'delay':'10ms'}
    l3 = {'bw':10, 'delay':'15ms'}

    topo = CustomTopo(linkopts1=l1, linkopts2=l2, linkopts3=l3, fanout=2)

    net = Mininet(topo, link=TCLink)
    net.start()
#   dumpNodeConnections(net.hosts)
    net.pingAll()
    
    hA = net.get('h110')
    hB = net.get('h001')
    print "Starting individual ping test"
    outputString = hA.cmd('ping', '-c6', hB.IP())
    print "output:{}".format(outputString)
    net.stop()

myTest()
