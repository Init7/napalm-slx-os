Value Filldown RouterID ([\d\.]+)
Value Filldown LocalAS (\d+)
Value NeighborAddress ([a-f\d\.:]{3,})
Value ASN (\d+)
Value State (\w+)
Value Time ([0-9ydhms]+)
Value Accepted (\d+)
Value Filtered (\d+)
Value Sent (\d+)
Value ToSend (\d+)

Start
  # Base Data
  ^\s+Router\s+ID:\s+${RouterID}\s+Local\s+AS\s+Number:\s+${LocalAS}
  # Entry
  ^\s+${NeighborAddress}\s+${ASN}\s+${State}\s+${Time}\s+${Accepted}\s+${Filtered}\s+${Sent}\s+${ToSend} -> Record
  ^\s+${ASN}\s+${State}\s+${Time}\s+${Accepted}\s+${Filtered}\s+${Sent}\s+${ToSend} -> Record
  ^\s+${NeighborAddress}
