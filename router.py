"""
[555 Comments]
Your router code and any other helper functions related to router should be written in this file
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import *
from pox.lib.addresses import *
from pox.lib.packet.icmp import *
from pox.lib.packet.ipv4 import *
import pox.lib.packet as pkt

log = core.getLogger()

"""
[555 Comments]
  Function : router_handler
  Input Parameters:
      rt_object : The router object. This will be initialized in the controller file corresponding to the scenario in __init__
                  function of tutorial class. Any data structures you would like to use for a router should be initialized
                  in the contoller file corresponding to the scenario.
      packet    : The packet that is received from the packet forwarding switch.
      packet_in : The packet_in object that is received from the packet forwarding switch
"""

class RouteEntry (object):
  def __init__ (self, port, nexthopIP):
    self.port = port
    self.nexthopIP = nexthopIP

def handleArpResponse(a, inport, rt_object, dpid):
    t = arp()
    t.hwtype = a.hwtype
    t.prototype = a.prototype
    t.hwlen = a.hwlen
    t.protolen = a.protolen
    t.opcode = arp.REPLY
    t.hwdst = a.hwsrc
    t.protodst = a.protosrc
    t.protosrc = a.protodst
    t.hwsrc = rt_object.arpTable[dpid][a.protodst]
    e = ethernet(type=ethernet.ARP_TYPE, src=rt_object.arpTable[dpid][a.protodst], dst=a.hwsrc)
    e.set_payload(t)
    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
    msg.in_port = inport
    log.debug("dpid %d: inport %d, replying for ARP from %s: mac for IP %s is %s" % (dpid, inport, str(a.protosrc), str(t.protosrc), str(t.hwsrc)))
    rt_object.connections[dpid].send(msg)
    
def handleArpWait(srcIP, rt_object, dpid):
    log.debug("dpid %d: process ARP wait packet for IP %s" % (dpid, str(srcIP)))
    while len(rt_object.arpWait[dpid][srcIP]) > 0:
        (bid, inport) = rt_object.arpWait[dpid][srcIP][0]
        msg = of.ofp_packet_out(buffer_id = bid, in_port = inport)
        out_port = rt_object.routeTable[dpid][srcIP].port
        msg.actions.append(of.ofp_action_dl_addr.set_src(rt_object.arpTable[dpid][rt_object.port_to_ip[dpid][out_port]]))
        msg.actions.append(of.ofp_action_dl_addr.set_dst(rt_object.arpTable[dpid][srcIP]))
        msg.actions.append(of.ofp_action_output(port = out_port))
        rt_object.connections[dpid].send(msg)
        log.debug("dpid %d: send wait ARP packet, destIP: %s, destMAC: %s, output port: %d" % (dpid, str(srcIP), str(rt_object.arpTable[dpid][srcIP]), rt_object.routeTable[dpid][srcIP].port))
        del rt_object.arpWait[dpid][srcIP][0]
    
def handleIcmpRequest(rt_object, dpid, packet, srcip, dstip, icmpType):
        pIcmp = icmp()
        pIcmp.type = icmpType
        if icmpType == pkt.TYPE_ECHO_REPLY:
            pIcmp.payload = packet.find('icmp').payload
        elif icmpType == pkt.TYPE_DEST_UNREACH:
            oriIp = packet.find('ipv4')
            d = oriIp.pack()
            d = d[:oriIp.hl * 4 + 8]
            d = struct.pack("!HH", 0, 0) + d
            pIcmp.payload = d
        pIp = ipv4()
        pIp.protocol = pIp.ICMP_PROTOCOL
        pIp.srcip = dstip
        pIp.dstip = srcip
        e = ethernet()
        e.src = packet.dst
        e.dst = packet.src
        e.type = e.IP_TYPE
        pIp.payload = pIcmp
        e.payload = pIp

        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
        msg.data = e.pack()
        msg.in_port = rt_object.routeTable[dpid][srcip].port
        rt_object.connections[dpid].send(msg)
        if icmpType == pkt.TYPE_ECHO_REPLY:
            log.debug("dpid %d: reply ping from %s to %s" % (dpid, str(srcip), str(dstip)))
        elif icmpType == pkt.TYPE_DEST_UNREACH:
            log.debug("dpid %d: packet from %s to %s is unreachable" % (dpid, str(srcip), str(dstip)))

def handleArpRequest(rt_object, target_ip, outport, dpid):
        t = arp()
        t.hwtype = t.HW_TYPE_ETHERNET
        t.prototype = t.PROTO_TYPE_IP
        t.hwlen = 6
        t.protolen = t.protolen
        t.opcode = t.REQUEST
        t.hwdst = ETHER_BROADCAST
        t.protodst = target_ip
        t.protosrc = rt_object.port_to_ip[dpid][outport]
        t.hwsrc = rt_object.arpTable[dpid][t.protosrc]
        e = ethernet(type=ethernet.ARP_TYPE, src=t.hwsrc, dst=ETHER_BROADCAST)
        e.set_payload(t)
        log.debug("dpid %d: port %s, sending ARP request for IP %s from %s" % (dpid, outport, str(t.protodst), str(t.protosrc)))
        msg = of.ofp_packet_out()
        msg.data = e.pack()
        msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
        msg.in_port = outport
        rt_object.connections[dpid].send(msg)

def router_handler(rt_object, dpid, packet, packet_in):
    
    if isinstance(packet.next, arp):
        a = packet.next
        if a.protosrc not in rt_object.arpTable[dpid]:
            rt_object.arpTable[dpid][a.protosrc] = a.hwsrc
            log.debug('dpid %d: adds arpTable IP %s to MAC %s' % (dpid, str(a.protosrc), str(a.hwsrc)))
        if a.opcode == arp.REQUEST and a.protodst in rt_object.gateways[dpid]: #arp to Router
            handleArpResponse(a, packet_in.in_port, rt_object, dpid)
        if a.protosrc in rt_object.arpWait[dpid] and (len(rt_object.arpWait[dpid][a.protosrc]) > 0): 
            handleArpWait(a.protosrc,rt_object,dpid)
            
    elif isinstance(packet.next, ipv4):
        n = packet.next
        log.debug("dpid %d: ipv4 packet inport %d, from %s to %s" % (dpid, packet_in.in_port, n.srcip, n.dstip))
        if n.dstip in rt_object.gateways[dpid]: #dst to router
            if (isinstance(n.next, icmp)) and (n.next.type == pkt.TYPE_ECHO_REQUEST):
                log.debug("ICMP packet comes to router")
                handleIcmpRequest(rt_object, dpid, packet, n.srcip, n.dstip, pkt.TYPE_ECHO_REPLY)
        else:
            if n.dstip in rt_object.routeTable[dpid]:
                nexthop_ip = rt_object.routeTable[dpid][n.dstip].nexthopIP
                out_port = rt_object.routeTable[dpid][n.dstip].port
                src_addr = rt_object.arpTable[dpid][rt_object.port_to_ip[dpid][out_port]]
                if nexthop_ip not in rt_object.arpTable[dpid]:
                    if nexthop_ip not in rt_object.arpWait[dpid]:
                        rt_object.arpWait[dpid][nexthop_ip] = []
                    entry = (packet_in.buffer_id, packet_in.in_port)
                    rt_object.arpWait[dpid][nexthop_ip].append(entry)
                    log.debug("dpid %d: packet from %s to %s is unknown for MAC of nexthop %s, adding to ArpWait" % (dpid, str(n.srcip), str(n.dstip), str(nexthop_ip)))
                    handleArpRequest(rt_object, nexthop_ip, out_port, dpid)
                else:
                    msg = of.ofp_packet_out(buffer_id=packet_in.buffer_id, in_port=packet_in.in_port)
                    msg.actions.append(of.ofp_action_dl_addr.set_src(src_addr))
                    msg.actions.append(of.ofp_action_dl_addr.set_dst(rt_object.arpTable[dpid][nexthop_ip]))
                    msg.actions.append(of.ofp_action_output(port=out_port))
                    rt_object.connections[dpid].send(msg)
                    log.debug("dpid %d: packet from %s to %s sent to port %d" % (dpid, str(n.srcip), str(n.dstip), out_port))

                    msg = of.ofp_flow_mod()
                    msg.match.dl_type = 0x0800
                    msg.match.nw_dst = n.dstip
                    msg.actions.append(of.ofp_action_dl_addr.set_src(src_addr))
                    msg.actions.append(of.ofp_action_dl_addr.set_dst(rt_object.arpTable[dpid][nexthop_ip]))
                    msg.actions.append(of.ofp_action_output(port=out_port))
                    rt_object.connections[dpid].send(msg)
            else:
                handleIcmpRequest(rt_object, dpid, packet, n.srcip, n.dstip, pkt.TYPE_DEST_UNREACH)
