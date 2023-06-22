Value Required Address ([\d\.]+)
Value Required MacAddress ([a-f\d\.]+)
Value Required L3Interface (\w+\s[0-9/]+)
Value Required L2Interface (\w+\s[0-9/]+)
Value Required Age ([\d:]+)
Value Required Type (\w+)

Start
  ^${Address}\s+${MacAddress}\s+${L3Interface}\s+${L2Interface}\s+${Age}\s+${Type} -> Record