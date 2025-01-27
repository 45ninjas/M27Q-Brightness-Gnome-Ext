# Yoinked from https://gist.github.com/wadimw/4ac972d07ed1f3b6f22a101375ecac41
#
# For Gigabyte M27Q KVM connected over USB-C
#
# Recreates messages captured with Wireshark from OSD Sidekick on Windows.
# Requires PyUSB.
# Further testing should be done.
# Code based mostly on https://www.linuxvoice.com/drive-it-yourself-usb-car-6/
# and https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
#
# Can be used on any platform that supports PyUSB.
#
# OSD getter, setter and KVM toggle based on @P403n1x87 findings (https://github.com/P403n1x87/m27q)

import usb.core
import usb.util
import typing as t
from time import sleep

class MonitorControl:
	def __init__(self):
		self._VID=0x2109 # (VIA Labs, Inc.)
		self._PID=0x8883 # USB Billboard Device
		self._dev=None
		self._usb_delay = 50/1000 # 50 ms sleep after every usb op
		self._min_brightness = 0
		self._max_brightness = 100
		self._min_volume = 0
		self._max_volume = 100
		

	# Find USB device, set config
	def __enter__(self):
		# Find device
		self._dev=usb.core.find(idVendor=self._VID, idProduct=self._PID)
		if self._dev is None:
			raise Exception(f"Device VID_{self._VID}&PID_{self._PID} not found")
		
		# Deach kernel driver
		self._had_driver = False
		try:
			if self._dev.is_kernel_driver_active(0):
				self._dev.detach_kernel_driver(0)
				self._had_driver = True
		except Exception as e:
			pass
		
		# Set config (1 as discovered with Wireshark)
		self._dev.set_configuration(1)
		return self

	# Optionally reattach kernel driver
	def __exit__(self, exc_type, exc_val, exc_tb):
		# Reattach kernel driver
		if self._had_driver:
			self._dev.attach_kernel_driver(0)
		# Release device
		usb.util.dispose_resources(self._dev)

	def usb_write(self, b_request: int, w_value: int, w_index: int, message: bytes):
		bm_request_type = 0x40
		if not self._dev.ctrl_transfer(bm_request_type, b_request, w_value, w_index, message) == len(message):
			raise IOError("Transferred message length mismatch")
		sleep(self._usb_delay)

	def usb_read(self, b_request: int, w_value: int, w_index: int, msg_length: int):
		bm_request_type = 0xC0
		data = self._dev.ctrl_transfer(bm_request_type, b_request, w_value, w_index, msg_length)
		sleep(self._usb_delay)
		return data

	def get_osd(self, data: t.List[int]):
		self.usb_write(
			b_request=178,
			w_value=0,
			w_index=0,
			message=bytearray([0x6E, 0x51, 0x81 + len(data), 0x01]) + bytearray(data),
		)
		data = self.usb_read(b_request=162, w_value=0, w_index=111, msg_length=12)
		return data[10]

	def set_osd(self, data: bytearray):
		self.usb_write(
			b_request=178,
			w_value=0,
			w_index=0,
			message=bytearray([0x6E, 0x51, 0x81 + len(data), 0x03] + data),
		)

	def set_brightness(self, brightness: int):
		self.set_osd(
			[
				0x10,
				0x00,
				max(self._min_brightness, min(self._max_brightness, brightness)),
			]
		)

	def get_brightness(self):
		return self.get_osd([0x10])

	def transition_brightness(self, to_brightness: int, step: int = 3):
		current_brightness = self.get_brightness()
		diff = abs(to_brightness - current_brightness)
		if current_brightness <= to_brightness:
			step = 1 * step # increase
		else:
			step = -1 * step # decrease
		while diff >= abs(step):
			current_brightness += step
			self.set_brightness(current_brightness)
			diff -= abs(step)
		# Set one last time
		if current_brightness != to_brightness:
			self.set_brightness(to_brightness)

	def get_kvm_status(self):
		return self.get_osd([224, 105])

	def set_kvm_status(self, status):
		self.set_osd([224, 105, status])

	def toggle_kvm(self):
		self.set_kvm_status(1 - self.get_kvm_status())
