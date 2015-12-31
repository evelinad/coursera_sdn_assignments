'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment: Layer-2 Firewall Application

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here ... '''
import pdb
import csv

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''



class Firewall (EventMixin):
    
    mac_deny_list = []

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

        with open(policyFile) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.mac_deny_list.append(row)



    def _handle_ConnectionUp (self, event):
        ''' Add your logic here ... '''
        for row in self.mac_deny_list:
            msg = of.ofp_flow_mod()
            msg.priority = of.OFP_DEFAULT_PRIORITY + 100
            msg.match = of.ofp_match(dl_src=EthAddr(row['mac_0']), dl_dst=EthAddr(row['mac_1']))
            msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
            event.connection.send(msg)
            log.debug("Installed firewall rule no {}".format(row['id']))

        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
