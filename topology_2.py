"""
Three devices on different networks and all connected by a single router

	host --- router ---- host
		   		|
		   		|
		   		|
		  	   host

"""

from mininet.topo import Topo

class MyTopo(Topo):

    def __init__(self):
	#Initialize the topology
        Topo.__init__(self)
        h1 = self.addHost( 'h1', ip="10.0.0.2/24", defaultRoute = "via 10.0.0.1" )
        h2 = self.addHost( 'h2', ip="20.0.0.2/24", defaultRoute = "via 20.0.0.1" )
        h3 = self.addHost( 'h3', ip="30.0.0.2/24", defaultRoute = "via 30.0.0.1" )
        r1 = self.addSwitch('r1')
      
        self.addLink(h1, r1, intfName1='h1-eth0', intfName2='r1-eth0')
        self.addLink(h2, r1, intfName1='h2-eth0', intfName2='r1-eth1')
        self.addLink(h3, r1, intfName1='h3-eth0', intfName2='r1-eth2')

topos = { 'mytopo':(lambda:MyTopo())}