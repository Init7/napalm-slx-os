Value Required VrfName ([\w\-]+)
Value Required VrfId (\d+)
Value Required V4Unicast (\w+|-)
Value Required V6Unicast (\w+|-)

Start
  ^${VrfName}\s+${VrfId}\s+${V4Unicast}\s+${V6Unicast} -> Record