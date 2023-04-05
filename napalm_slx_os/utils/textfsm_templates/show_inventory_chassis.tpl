Value SID ([\w\-_]+)
Value PN ([\w\-_0-9]+)
Value SN ([\w\-_0-9]+)

Start
  ^SID:${SID}
  ^PN:${PN}\s+SN:${SN}