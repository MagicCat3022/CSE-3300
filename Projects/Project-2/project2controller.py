# Final Skeleton
#
# Hints:
#
# To check the source and destination of an IP packet, you can use
# the header information... For example:
#
# ip_header = packet.find('ipv4')
#
# if ip_header.srcip == "1.1.1.1":
#   print "Packet is from 1.1.1.1"
#
# Important Note: the "is" comparison DOES NOT work for IP address
# comparisons in this way. You must use ==.
#
# To send an OpenFlow Message telling a switch to send packets out a
# port, do the following, replacing <PORT> with the port number the
# switch should send the packets out:
#
#    msg = of.ofp_flow_mod()
#    msg.match = of.ofp_match.from_packet(packet)
#    msg.idle_timeout = 30
#    msg.hard_timeout = 30
#
#    msg.actions.append(of.ofp_action_output(port = <PORT>))
#    msg.data = packet_in
#    self.connection.send(msg)
#
# To drop packets, simply omit the action.
#
import sys
import os
sys.path.append(os.path.abspath('/home/mustafa/Github/pox'))

from pox.core import core
import pox.openflow.libopenflow_01 as of
from typing import List, cast, TYPE_CHECKING
from pox.lib.addresses import IPAddr
from pox.lib.packet.ipv4 import ipv4

UNTRUSTED_IP = IPAddr("123.45.67.89")
SERVER_IP = IPAddr("10.5.5.50")
NETWORK_HOSTS = {
	IPAddr("10.1.1.10"),
	IPAddr("10.2.2.20"),
	IPAddr("10.3.3.30"),
	IPAddr("10.5.5.50"),
	IPAddr("123.45.67.89")
}
INTERNAL_HOSTS = {
	IPAddr("10.1.1.10"),
	IPAddr("10.2.2.20"),
	IPAddr("10.3.3.30"),
	IPAddr("10.5.5.50")
}
INTERNAL_SWITCH_TO_HOST = {
	1: IPAddr("10.1.1.10"),
	2: IPAddr("10.2.2.20"),
	3: IPAddr("10.3.3.30"),
	5: IPAddr("10.5.5.50")
}
S4_DEST_TO_PORT = {
	IPAddr("10.1.1.10"): 1,
	IPAddr("10.2.2.20"): 2,
	IPAddr("10.3.3.30"): 3,
	IPAddr("10.5.5.50"): 5,
	IPAddr("123.45.67.89"): 9
}
IP_TO_HOST = {
	IPAddr("10.1.1.10"): "h1",
	IPAddr("10.2.2.20"): "h2",
	IPAddr("10.3.3.30"): "h3",
	IPAddr("10.5.5.50"): "h5",
	IPAddr("123.45.67.89"): "h4"
}


class Final(object):
	"""
	A Firewall object is created for each switch that connects.
	A Connection object for that switch is passed to the __init__ function.
	"""

	def __init__(self, connection):
		# Keep track of the connection to the switch so that we can
		# send it messages!
		self.connection = connection

		# This binds our PacketIn event listener
		connection.addListeners(self)

	def send_out(self, packet, packet_in, port):
		msg = of.ofp_flow_mod()
		msg.match = of.ofp_match.from_packet(packet)
		msg.idle_timeout = 30
		msg.hard_timeout = 30
		actions = cast(List[of.ofp_action_base], msg.actions)
		actions.append(of.ofp_action_output(port=port))
		msg.data = packet_in
		self.connection.send(msg)
		return

	def send_drop(self, packet, packet_in):
		msg = of.ofp_flow_mod()
		msg.match = of.ofp_match.from_packet(packet)
		msg.idle_timeout = 30
		msg.hard_timeout = 30
		msg.data = packet_in
		self.connection.send(msg)
		return

	def do_final(self, packet, packet_in, port_on_switch, switch_id):
		# This is where you'll put your code.
		#   - port_on_switch: represents the port that the packet was received on.
		#   - switch_id represents the id of the switch that received the packet.
		#      (for example, s1 would have switch_id == 1, s2 would have switch_id == 2, etc...)
		# You should use these to determine where a packet came from. To figure out where a packet
		# is going, you can use the IP header information.
		ip_header = packet.find("ipv4")

		if ip_header is None:
			ipv6_header = packet.find("ipv6")

			if ipv6_header is None:
				self.send_out(packet, packet_in, of.ofp_port_rev_map["OFPP_FLOOD"])

			return

		src_ip = IPAddr(ip_header.srcip)
		dst_ip = IPAddr(ip_header.dstip)

		print(f"Switch: {switch_id}, Port: {port_on_switch}, Packet: (src: {IP_TO_HOST[src_ip]}, dst: {IP_TO_HOST[dst_ip]})")

		if src_ip not in NETWORK_HOSTS:
			print("Blocking Unknown Source")
			self.send_drop(packet, packet_in)
			return
		
		if dst_ip not in NETWORK_HOSTS:
			print("Blocking Unknown Destination")
			self.send_drop(packet, packet_in)
			return

		# Handle untrusted host (h4)
		if src_ip == UNTRUSTED_IP:
			if dst_ip == SERVER_IP: # h4 cannot talk to server
				print("Blocking Untrusted IP packet to Server")
				self.send_drop(packet, packet_in)
				return

			# Block ICMP from h4 to internal hosts
			if ip_header.protocol == ipv4.ICMP_PROTOCOL and dst_ip in INTERNAL_HOSTS:
				print("Blocking Untrusted ICMP packet to Internal Hosts")
				self.send_drop(packet, packet_in)
				return

		# Handle main switch (s4)
		if switch_id == 4:
			out_port = S4_DEST_TO_PORT.get(dst_ip) # get the output port for the destination IP
			self.send_out(packet, packet_in, out_port)
			return

		# Handle internal switches
		if switch_id in INTERNAL_SWITCH_TO_HOST:
			switch_host = INTERNAL_SWITCH_TO_HOST[switch_id] # get the host IP for this switch

			if dst_ip == switch_host: # packet target is this switch's host
				out_port = 9
				print()
			else:
				out_port = 2 # forward to main switch
			
			self.send_out(packet, packet_in, out_port)
			return

		print("Dropping packet by default")
		self.send_drop(packet, packet_in)
		return

	def _handle_PacketIn(self, event):
		"""
		Handles packet in messages from the switch.
		"""
		packet = event.parsed  # This is the parsed packet data.
		if not packet.parsed:
			# log.warning("Ignoring incomplete packet")
			return

		packet_in = event.ofp  # The actual ofp_packet_in message.
		self.do_final(packet, packet_in, event.port, event.dpid)


art = '''
⠀⠀⠀⢀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣄⠀⠀⠀⠀⢹⡛⠉⠛⠓⠲⢤⣄⡀⠀⠀⠀⠀⠀⢀⡴⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣏
⠀⠀⠀⣸⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣧⡀⠀⠀⠘⣧⠀⠀⠀⠀⠀⠈⠛⢦⣀⠀⠀⢀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡏
⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣆⡀⠀⠸⣆⠀⠀⠀⠀⠀⠀⠀⠙⠳⣤⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡇
⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣿⠶⠚⠛⠏⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡇
⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠶⢯⣭⣤⣤⡤⠤⠤⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡇
⠀⠀⠀⡧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡗
⠀⠀⠀⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡟⠀
⠀⠀⠀⠘⣧⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣤⣴⣶⠶⠶⠲⣶⠶⠶⠀⠀⠀⠀⠀⠀⣼⠃⠀
⠀⠀⠀⠀⠹⡄⠀⠀⠀⠈⠉⡟⠉⠁⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡀⠀⠀⠹⡧⠀⠀⠀⠀⢀⣠⠾⠉⠀⠀
⢀⣀⣀⠀⠀⠻⣦⠀⠀⠀⢸⠃⠀⠀⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠄⠀⠀⠀⢹⠀⠀⠠⡦⠿⠟⠲⠶⢶⡄
⠀⢻⡍⠛⠙⠛⠛⠻⠀⠀⣾⠁⠀⠀⠀⢸⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⣰⠞⠁
⠀⠀⠹⢦⡄⠀⠀⠀⠀⠀⣻⡄⠀⠀⠀⠈⠻⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⠟⠛⠁⠀⠀⠀⠀⠼⠀⠀⠀⠀⠀⣠⡞⠉⠀⠀
⠀⠀⠀⠀⠙⣷⠄⠀⣠⣤⡈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡆⢀⡤⠀⠀⠀⢺⣇⠀⠀⠀⠀
⠀⠀⠀⠀⣰⠇⠀⠘⠃⢸⡧⠶⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⣤⠀⠀⠀⠀⠀⠛⠹⠷⠋⠀⠀⠀⠀⠀⠙⣦⠀⠀⠀
⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠦⣄⡤⠾⠋⠙⠛⠓⠲⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠉⣿⠀⠀
⠀⠀⠀⠸⠷⠤⠤⠴⠶⠾⢦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⠞⠃⠶⠶⠶⠞⠛⠛⠉⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢻⣶⣶⣴⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠶⠗⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⡄⠈⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣁⣤⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀
'''

def launch():
	"""
	Starts the component
	"""
	print(art)
	print()
	def start_switch(event):
		Final(event.connection)

	core.openflow.addListenerByName("ConnectionUp", start_switch)
