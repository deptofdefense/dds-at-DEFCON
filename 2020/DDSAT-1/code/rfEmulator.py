import binascii # needed for conversions


class RFEmulator:
    '''A class to emulate RF encoding and decoding over Twitch chat '''

    def __init__(self):
        ''' initalization'''

    def encodeHex(self, hexStr):
        '''Accepts a hex string and returns the manchester modulated base64 string'''

        # creates the empty strings to use
        binStr = ""
        manStr = ""
        newBytes = 0

        # converts the hex string to binary
        for c in hexStr:
            try:
                binStr = binStr + format(int(c, 16), '04b')
            except ValueError:
                binStr = binStr + "0000"
                print("Warning, encoding error")

        #print(binStr)
        
        # converts to a manchester format: 1 becomes 10 and 0 becomes 01
        for c in binStr:
            if c == "1":
                manStr = manStr + "10"
            else:
                manStr = manStr + "01"

        #print(manStr)

        # converts to a byte array for base64
        newBytes = int(manStr, 2).to_bytes((len(manStr) + 7) // 8, byteorder='big')

        #print(binascii.b2a_base64(newBytes).decode('latin1'))

        return binascii.b2a_base64(newBytes).decode('latin1')

    def decodeManBase(self, baseStr):
        '''Accepts a manchester modulated base64 string and returns the decoded hex string'''

        # creates the empty strings to use
        binStr = ""
        manStr = ""
        hexStr = ""
        #print(baseStr)

        # base64 decoded string as hex
        temp = binascii.a2b_base64(baseStr)
        #print(str(temp))
        temp = binascii.b2a_hex(temp).decode()
        #print(str(temp))


        # convert hex to binary manchester
        for c in str(temp):
            try:
                manStr = manStr + format(int(c, 16), '04b')
            except ValueError:
                manStr = manStr + "0000"
                print("Warning, decoding error")

        #print(manStr)

        # convert manchester to normal binary
        for c in range(0, len(manStr), 2):
            if manStr[c:c+2] == '10':
                binStr = binStr + '1'
            else:
                binStr = binStr + '0'

        #print(f"binStr: {binStr}")

        # convert back to hex string
        hexStr = format(int(binStr, 2), 'x')

        #print(f"hexstr: {hexStr}")

        return hexStr
        