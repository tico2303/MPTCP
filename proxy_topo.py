""" Proxy Topology

1 hosts connected to proxy host that is connected to two switches that connect to a host.

   host1(client) -- host2(proxy) --- switch1 , switch2 --- host3(server)

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class ProxyTopo( Topo ):
    "Proxy topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        client = self.addHost( 'client' )
        proxy = self.addHost( 'proxy' )
	sw1 = self.addSwitch( 'sw1' )
	sw2 = self.addSwitch( 'sw2' )
        server = self.addHost( 'server' )

        # Add links
        self.addLink( client, proxy )
        self.addLink( proxy, sw1 )
        self.addLink( proxy, sw2 )
        self.addLink( sw1, server )
        self.addLink( sw2, server )

topos = { 'proxytopo': ( lambda: ProxyTopo() ) }
