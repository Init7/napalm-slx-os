Value Required RecordNumber (\d+)
Value Required IPAddress ([\d\.]+)
Value Required ASN (\d+)
Value Description (.*)
Value BGPType (\w+)
Value RouterID ([\d\.]+)
Value VRF ([\w_-]+)
Value State (\w+)
Value Time ([0-9ydhms]+)
Value KeepAliveTime (\d+)
Value HoldTime (\d+)
Value LocalAddress ([\d\.]+)
Value LocalPort (\d+)
Value RemoteAddress ([\d\.]+)
Value RemotePort (\d+)
Value RemovePrivateAs (yes|no)
Value MsgSentOpen (\d+)
Value MsgSentUpdate (\d+)
Value MsgSentKeepAlive (\d+)
Value MsgSentNotification (\d+)
Value MsgSentRefresh (\d+)
Value MsgRecvOpen (\d+)
Value MsgRecvUpdate (\d+)
Value MsgRecvKeepAlive (\d+)
Value MsgRecvNotification (\d+)
Value MsgRecvRefresh (\d+)

Start
  # Record begin
  ^\d+\s+IP.* -> Continue.Record
  ^${RecordNumber}\s+IP Address:\s+${IPAddress},\s+AS:\s+${ASN}\s+\(${BGPType}\),\s+RouterID:\s+${RouterID},\s+VRF:\s+${VRF}
  ^\s+Description: ${Description}
  ^\s+State: ${State}, Time: ${Time}, KeepAliveTime: ${KeepAliveTime}, HoldTime: ${HoldTime}
  ^\s+Local\s+host:\s+${LocalAddress},\s+Local\s+Port:\s+${LocalPort}
  ^\s+Remote\s+host:\s+${RemoteAddress},\s+Remote\s+Port:\s+${RemotePort}
  ^\s+RemovePrivateAs[\s:]+${RemovePrivateAs}
  ^\s+Sent[\s:]+${MsgSentOpen}\s+${MsgSentUpdate}\s+${MsgSentKeepAlive}\s+${MsgSentNotification}\s+${MsgSentRefresh}
  ^\s+Received[\s:]+${MsgRecvOpen}\s+${MsgRecvUpdate}\s+${MsgRecvKeepAlive}\s+${MsgRecvNotification}\s+${MsgRecvRefresh}