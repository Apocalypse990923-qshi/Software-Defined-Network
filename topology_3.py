"""
A complex containing 3 routers, 5 switches, 5 subnets and 15 hosts.
"""

from mininet.topo import Topo

class MyTopo(Topo):
    "Simple topology example."

    def __init__(self):
        Topo.__init__(self)
        r1 = self.addSwitch('r1')
        r2 = self.addSwitch('r2')
        r3 = self.addSwitch('r3')
        
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')
        s8 = self.addSwitch('s8')
        
        h9 = self.addHost('h9',ip = "172.17.16.2/24", defaultRoute="via 172.17.16.1")
        h10 = self.addHost('h10',ip = "172.17.16.3/24", defaultRoute="via 172.17.16.1")
        h11 = self.addHost('h11',ip = "172.17.16.4/24", defaultRoute="via 172.17.16.1")
        
        h12 = self.addHost('h12',ip = "10.0.0.2/25", defaultRoute="via 10.0.0.1")
        h13 = self.addHost('h13',ip = "10.0.0.3/25", defaultRoute="via 10.0.0.1")
        h14 = self.addHost('h14',ip = "10.0.0.4/25", defaultRoute="via 10.0.0.1")
        
        h15 = self.addHost('h15',ip = "10.0.0.130/25", defaultRoute="via 10.0.0.129")
        h16 = self.addHost('h16',ip = "10.0.0.131/25", defaultRoute="via 10.0.0.129")
        h17 = self.addHost('h17',ip = "10.0.0.132/25", defaultRoute="via 10.0.0.129")
        
        h18 = self.addHost('h18',ip = "20.0.0.2/25", defaultRoute="via 20.0.0.1")
        h19 = self.addHost('h19',ip = "20.0.0.3/25", defaultRoute="via 20.0.0.1")
        h20 = self.addHost('h20',ip = "20.0.0.4/25", defaultRoute="via 20.0.0.1")
        
        h21 = self.addHost('h21',ip = "20.0.0.130/25", defaultRoute="via 20.0.0.129")
        h22 = self.addHost('h22',ip = "20.0.0.131/25", defaultRoute="via 20.0.0.129")
        h23 = self.addHost('h23',ip = "20.0.0.132/25", defaultRoute="via 20.0.0.129")
        
        self.addLink(r1, s4, intfName1='r1-eth0', intfName2='s4-eth0')
        
        self.addLink(r2, s5, intfName1='r2-eth0', intfName2='s5-eth0')
        self.addLink(r2, s6, intfName1='r2-eth1', intfName2='s6-eth0')
        
        self.addLink(r3, s7, intfName1='r3-eth0', intfName2='s7-eth0')
        self.addLink(r3, s8, intfName1='r3-eth1', intfName2='s8-eth0')
        
        self.addLink(r1, r2, intfName1='r1-eth1', intfName2='r2-eth2')
        self.addLink(r1, r3, intfName1='r1-eth2', intfName2='r3-eth2')
        
        
        self.addLink(h9, s4, intfName1='h9-eth0', intfName2='s4-eth1')
        self.addLink(h10, s4, intfName1='h10-eth0', intfName2='s4-eth2')
        self.addLink(h11, s4, intfName1='h11-eth0', intfName2='s4-eth3')
        
        self.addLink(h12, s5, intfName1='h12-eth0', intfName2='s5-eth1')
        self.addLink(h13, s5, intfName1='h13-eth0', intfName2='s5-eth2')
        self.addLink(h14, s5, intfName1='h14-eth0', intfName2='s5-eth3')
        
        self.addLink(h15, s6, intfName1='h15-eth0', intfName2='s6-eth1')
        self.addLink(h16, s6, intfName1='h16-eth0', intfName2='s6-eth2')
        self.addLink(h17, s6, intfName1='h17-eth0', intfName2='s6-eth3')
        
        self.addLink(h18, s7, intfName1='h18-eth0', intfName2='s7-eth1')
        self.addLink(h19, s7, intfName1='h19-eth0', intfName2='s7-eth2')
        self.addLink(h20, s7, intfName1='h20-eth0', intfName2='s7-eth3')
        
        self.addLink(h21, s8, intfName1='h21-eth0', intfName2='s8-eth1')
        self.addLink(h22, s8, intfName1='h22-eth0', intfName2='s8-eth2')
        self.addLink(h23, s8, intfName1='h23-eth0', intfName2='s8-eth3')
        
topos = { 'mytopo':(lambda:MyTopo())}