"""
[555 Comments]
Your switch code and any other helper functions related to switch should be written in this file
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import *
from pox.lib.addresses import *
from pox.lib.packet.icmp import *
from pox.lib.packet.ipv4 import *

log = core.getLogger()

"""
[555 Comments]
  Function : switch_handler
  Input Parameters:
      sw_object : The switch object. This will be initialized in the controller file corresponding to the scenario in __init__
                  function of tutorial class. Any data structures you would like to use for a switch should be initialized
                  in the contoller file corresponding to the scenario.
      packet    : The packet that is received from the packet forwarding switch.
      packet_in : The packet_in object that is received from the packet forwarding switch
"""
def switch_handler(sw_object, dpid, packet, packet_in):
    if packet.src not in sw_object.mac_to_port[dpid]:
        sw_object.mac_to_port[dpid][packet.src] = packet_in.in_port
        log.debug('Switch dpid %d: learns port %d as source port' % (dpid, sw_object.mac_to_port[dpid][packet.src]))
        
    if packet.dst in sw_object.mac_to_port[dpid]:
        log.debug('Switch dpid %d: sending packet to port %d' % (dpid, sw_object.mac_to_port[dpid][packet.dst]))
        sw_object.resend_packet(packet_in, sw_object.mac_to_port[dpid][packet.dst])
        log.debug("Installing flow...")
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match(dl_src = packet.src, dl_dst = packet.dst)
        msg.actions.append(of.ofp_action_output(port = sw_object.mac_to_port[dpid][packet.dst]))
        sw_object.connections[dpid].send(msg)
        log.debug('Switch dpid %d: adding flow from src %s to dst %s, port %d' % (dpid, packet.src, packet.dst, sw_object.mac_to_port[dpid][packet.dst]))
    else:
        log.debug('Switch dpid %d: flooding' % (dpid))
        sw_object.resend_packet(packet_in, of.OFPP_ALL)