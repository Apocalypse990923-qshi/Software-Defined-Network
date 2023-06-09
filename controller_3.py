# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
[555 Comments]
This is the controller file corresponding to scenario 3.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import *
from pox.lib.addresses import *
from pox.lib.packet.icmp import *
from pox.lib.packet.ipv4 import *
from switch import *
from router import *

log = core.getLogger()

class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    """
    [555 Comments]
    In scenario 3, there are many routers and switches. You need to classify a device as a router or a switch based on its DPID
    Remember one thing very carefully. The DPID gets assigned based on how you define tour devices in the topology file.
    So, be careful and DPID here should be coordinated with your definition in topology file.
    For the details of port info table, routing table, of different routers look into the project description document provided.
    Initialize any other data structures you wish to for the routers and switches here

    A word of caution:
    Your router and switch code should be the same for all scenarios. So, be careful to design your data structures for router
    and switches in such a way that your single piece of switch code and router code along with your data structure design
    should work for all the scenarios
    """
    self.connections={}
    self.arpTable = {}
    self.routeTable = {}
    self.arpWait = {}
    self.gateways = {}
    self.port_to_ip={}
    self.mac_to_port = {}
    

  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)
    
  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    """
    [555 Comments]
    You need to classify a device as either switch or router based on its DPID received in the connection object during
    initialization in __init__ function in tutorial class. Based on the device type you need to call the respective function
    Here is the pseudo code to write

    if packet received from device type is switch:
      invoke switch_handler and pass the object (i.e., self) and the packet and packet_in
    else: (if it is not switch, it means router. We have only two kinds of devices, one is switch and one is router)
      invoke router_handler and pass the object (i.e., self) and the packet and packet_in
    """
    dpid = event.connection.dpid
    #log.debug('DPID %d dealing with packets' % (dpid))
    if dpid not in self.connections:
        self.connections[dpid] = event.connection
    
    if dpid >= 4:    #it's switch
        if dpid not in self.mac_to_port:
            self.mac_to_port[dpid] = {}
        log.debug('Switch %d dealing with packets' % (dpid))
        switch_handler(self,dpid,packet,packet_in)
        return
    
    #it's router
    if dpid not in self.gateways:
        #self.gateways[dpid]=[IPAddr('172.17.16.1'), IPAddr('20.0.0.1'), IPAddr('10.0.0.1'), IPAddr('20.0.0.129'), IPAddr('10.0.0.129')]
        if dpid == 1: #router1
          self.gateways[dpid]=[IPAddr('172.17.16.1'), IPAddr('192.168.0.1'),IPAddr('192.168.0.5')]
        elif dpid == 2: #router2
          self.gateways[dpid]=[IPAddr('10.0.0.1'), IPAddr('10.0.0.129'),IPAddr('192.168.0.2')]
        elif dpid == 3: #router3
          self.gateways[dpid]=[IPAddr('20.0.0.1'), IPAddr('20.0.0.129'),IPAddr('192.168.0.6')]
    
    if dpid not in self.arpTable and dpid in self.gateways:
        self.arpTable[dpid]={}
        #temp = self.gateways[dpid]
        
        if dpid == 1:
          self.arpTable[dpid][IPAddr('172.17.16.1')] = EthAddr("02:00:de:ad:be:11")
          self.arpTable[dpid][IPAddr('192.168.0.1')] = EthAddr("02:00:de:ad:be:12")
          self.arpTable[dpid][IPAddr('192.168.0.5')] = EthAddr("02:00:de:ad:be:13")
        elif dpid == 2:
          self.arpTable[dpid][IPAddr('10.0.0.1')] = EthAddr("02:00:de:ad:be:21")
          self.arpTable[dpid][IPAddr('10.0.0.129')] = EthAddr("02:00:de:ad:be:22")
          self.arpTable[dpid][IPAddr('192.168.0.2')] = EthAddr("02:00:de:ad:be:23")
        elif dpid == 3:
          self.arpTable[dpid][IPAddr('20.0.0.1')] = EthAddr("02:00:de:ad:be:31")
          self.arpTable[dpid][IPAddr('20.0.0.129')] = EthAddr("02:00:de:ad:be:32")
          self.arpTable[dpid][IPAddr('192.168.0.6')] = EthAddr("02:00:de:ad:be:33")
        
    if dpid not in self.routeTable and dpid in self.gateways:
        self.routeTable[dpid]={}
        if dpid == 1:
          self.routeTable[dpid][IPAddr('172.17.16.2')] = RouteEntry(1, IPAddr('172.17.16.2'))
          self.routeTable[dpid][IPAddr('172.17.16.3')] = RouteEntry(1, IPAddr('172.17.16.3'))
          self.routeTable[dpid][IPAddr('172.17.16.4')] = RouteEntry(1, IPAddr('172.17.16.4'))
          
          self.routeTable[dpid][IPAddr('192.168.0.2')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.1')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.2')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.3')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.4')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.129')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.130')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.131')] = RouteEntry(2, IPAddr('192.168.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.132')] = RouteEntry(2, IPAddr('192.168.0.2'))
          
          self.routeTable[dpid][IPAddr('192.168.0.6')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.1')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.2')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.3')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.4')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.129')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.130')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.131')] = RouteEntry(3, IPAddr('192.168.0.6'))
          self.routeTable[dpid][IPAddr('20.0.0.132')] = RouteEntry(3, IPAddr('192.168.0.6'))
          
        elif dpid == 2:
          self.routeTable[dpid][IPAddr('10.0.0.2')] = RouteEntry(1, IPAddr('10.0.0.2'))
          self.routeTable[dpid][IPAddr('10.0.0.3')] = RouteEntry(1, IPAddr('10.0.0.3'))
          self.routeTable[dpid][IPAddr('10.0.0.4')] = RouteEntry(1, IPAddr('10.0.0.4'))
          self.routeTable[dpid][IPAddr('10.0.0.130')] = RouteEntry(2, IPAddr('10.0.0.130'))
          self.routeTable[dpid][IPAddr('10.0.0.131')] = RouteEntry(2, IPAddr('10.0.0.131'))
          self.routeTable[dpid][IPAddr('10.0.0.132')] = RouteEntry(2, IPAddr('10.0.0.132'))
          
          self.routeTable[dpid][IPAddr('192.168.0.1')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('172.17.16.1')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('172.17.16.2')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('172.17.16.3')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('172.17.16.4')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('192.168.0.5')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('192.168.0.6')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.1')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.2')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.3')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.4')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.129')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.130')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.131')] = RouteEntry(3, IPAddr('192.168.0.1'))
          self.routeTable[dpid][IPAddr('20.0.0.132')] = RouteEntry(3, IPAddr('192.168.0.1'))
          
        else:
          self.routeTable[dpid][IPAddr('20.0.0.2')] = RouteEntry(1, IPAddr('20.0.0.2'))
          self.routeTable[dpid][IPAddr('20.0.0.3')] = RouteEntry(1, IPAddr('20.0.0.3'))
          self.routeTable[dpid][IPAddr('20.0.0.4')] = RouteEntry(1, IPAddr('20.0.0.4'))
          self.routeTable[dpid][IPAddr('20.0.0.130')] = RouteEntry(2, IPAddr('20.0.0.130'))
          self.routeTable[dpid][IPAddr('20.0.0.131')] = RouteEntry(2, IPAddr('20.0.0.131'))
          self.routeTable[dpid][IPAddr('20.0.0.132')] = RouteEntry(2, IPAddr('20.0.0.132'))
          
          self.routeTable[dpid][IPAddr('192.168.0.5')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('172.17.16.1')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('172.17.16.2')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('172.17.16.3')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('172.17.16.4')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('192.168.0.1')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('192.168.0.2')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.1')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.2')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.3')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.4')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.129')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.130')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.131')] = RouteEntry(3, IPAddr('192.168.0.5'))
          self.routeTable[dpid][IPAddr('10.0.0.132')] = RouteEntry(3, IPAddr('192.168.0.5'))
          
    if dpid not in self.arpWait and dpid in self.gateways:
        self.arpWait[dpid]={}
    if dpid not in self.port_to_ip and dpid in self.gateways:
        self.port_to_ip[dpid]={}
        if dpid == 1:
          self.port_to_ip[dpid][1]=IPAddr('172.17.16.1')
          self.port_to_ip[dpid][2]=IPAddr('192.168.0.1')
          self.port_to_ip[dpid][3]=IPAddr('192.168.0.5')
        if dpid == 2:
          self.port_to_ip[dpid][1]=IPAddr('10.0.0.1')
          self.port_to_ip[dpid][2]=IPAddr('10.0.0.129')
          self.port_to_ip[dpid][3]=IPAddr('192.168.0.2')
        if dpid == 3:
          self.port_to_ip[dpid][1]=IPAddr('20.0.0.1')
          self.port_to_ip[dpid][2]=IPAddr('20.0.0.129')
          self.port_to_ip[dpid][3]=IPAddr('192.168.0.6')
        
    log.debug('Router %d dealing with packets' % (dpid))
    router_handler(self, dpid, packet, packet_in)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    #log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)