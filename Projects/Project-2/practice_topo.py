from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

class BaseTopo(Topo):
    def build(self):
        # Creating switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
   

        # Creating Hosts with specified MAC addresses, IPs, and default routes
        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.1.1.10/24', defaultRoute="h1-eth0")
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.1.1.11/24', defaultRoute="h2-eth0")
        h3 = self.addHost('h3', mac='00:00:00:00:00:03', ip='123.66.66.66/24', defaultRoute="h3-eth0")
    

        # Adding links with specified ports, using port 0 for hosts as per the example
        self.addLink(h1, s1, port1=0, port2=1)
        self.addLink(h2, s1, port1=0, port2=2)
        self.addLink(h3, s2, port1=0, port2=1)
        # Connect switches to switches with higher port numbers
        self.addLink(s1, s2, port1=3, port2=2)


def configure():
    topo = BaseTopo()
    # Connect to the POX controller at localhost on the default port 6633
    net = Mininet(topo=topo, controller=RemoteController('c0', ip='127.0.0.1', port=6633), switch=OVSSwitch)
    net.start()

    # Print the status of hosts and switches
    print("Hosts and switches status:")
    for host in net.hosts:
        print(host.name, host.IP(), host.MAC())
    for switch in net.switches:
        print(switch.name, switch.dpid)

    CLI(net)  # Start command line interface
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    configure()