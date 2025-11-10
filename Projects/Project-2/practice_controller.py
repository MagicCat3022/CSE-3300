# Final Skeleton
#

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
#    actions = cast(List[of.ofp_action_base], msg.actions)
#    actions.append(of.ofp_action_output(port = <PORT>))
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

# log = core.getLogger()


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
		ip = packet.find("ipv4")
		if ip is None:
			ipv2 = packet.find("ipv6")
			if ipv2 is None:
				print("Non IP")
				self.send_out(packet, packet_in, of.ofp_port_rev_map["OFPP_FLOOD"])
			return
		if switch_id == 1:
			print("From switch 1")
			if ip.dstip == "10.1.1.10":
				self.send_out(packet, packet_in, 1)
				return
			if ip.dstip == "10.1.1.11":
				self.send_out(packet, packet_in, 2)
			else:
				self.send_out(packet, packet_in, 3)
				return
		elif switch_id == 2:
			print("From switch 2")
			icmp = packet.find("icmp")
			if ip.srcip == "123.66.66.66":
				if icmp is not None:
					self.send_drop(packet, packet_in)
					return
			if ip.dstip == "123.66.66.66":
				self.send_out(packet, packet_in, 1)
				return
			else:
				self.send_out(packet, packet_in, 2)
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


def launch():
	"""
	Starts the component
	"""

	def start_switch(event):
		# log.debug("Controlling %s" % (event.connection,))
		Final(event.connection)

	core.openflow.addListenerByName("ConnectionUp", start_switch)
