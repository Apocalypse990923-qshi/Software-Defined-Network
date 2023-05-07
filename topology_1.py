"""
Three devices on same network and all connected by a switch

	host --- switch ---- host
		   		|
		   		|
		   		|
		  	   host

"""

from mininet.topo import Topo

class MyTopo(Topo):
    #"Simple topology example."

    def __init__(self):
        #"Create custom topology."
        Topo.__init__(self)
        h1 = self.addHost( 'h1', ip="10.0.0.2/24", defaultRoute = "via 10.0.0.1" )
        h2 = self.addHost( 'h2', ip="10.0.0.3/24", defaultRoute = "via 10.0.0.1" )
        h3 = self.addHost( 'h3', ip="10.0.0.4/24", defaultRoute = "via 10.0.0.1" )
        s1 = self.addSwitch('s1')
        
        self.addLink(h1, s1, intfName1='h1-eth0', intfName2='s1-eth0')
        self.addLink(h2, s1, intfName1='h2-eth0', intfName2='s1-eth1')
        self.addLink(h3, s1, intfName1='h3-eth0', intfName2='s1-eth2')

topos = { 'mytopo':(lambda:MyTopo())}