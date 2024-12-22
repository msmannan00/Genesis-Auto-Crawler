from enum import Enum


class network_type(Enum):
  CLEARNET = "clearnet"
  I2P = "i2p"
  ONION = "onion"
  INVALID = "invalid"
