'''
Coursera:
- Software Defined Networking (SDN) course
-- Network Virtualization

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os

log = core.getLogger()


class TopologySlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Slicing Module")


    """This event will be raised each time a switch will connect to the controller"""
    def _handle_ConnectionUp(self, event):

        # Use dpid to differentiate between switches (datapath-id)
        # Each switch has its own flow table. As we'll see in this
        # example we need to write different rules in different tables.
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)

        """ Add your logic here """
        def add_drop_rule(mac_src, mac_dst):
            msg = of.ofp_flow_mod()
            msg.priority = of.OFP_DEFAULT_PRIORITY + 200
            msg.match = of.ofp_match(dl_src=mac_src, dl_dst=mac_dst)
            msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
            event.connection.send(msg)

        sw_dpid = {1: '00-00-00-00-00-01',
                   2: '00-00-00-00-00-02',
                   3: '00-00-00-00-00-03',
                   4: '00-00-00-00-00-04'}

        if dpid == sw_dpid[1]:
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:01'), mac_dst=EthAddr('00:00:00:00:00:02'))
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:02'), mac_dst=EthAddr('00:00:00:00:00:01'))
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:01'), mac_dst=EthAddr('00:00:00:00:00:04'))
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:02'), mac_dst=EthAddr('00:00:00:00:00:03'))
        if dpid == sw_dpid[4]:
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:03'), mac_dst=EthAddr('00:00:00:00:00:04'))
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:04'), mac_dst=EthAddr('00:00:00:00:00:03'))
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:03'), mac_dst=EthAddr('00:00:00:00:00:02'))
            add_drop_rule(mac_src=EthAddr('00:00:00:00:00:04'), mac_dst=EthAddr('00:00:00:00:00:01'))


def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Topology Slicing module
    '''
    core.registerNew(TopologySlice)
