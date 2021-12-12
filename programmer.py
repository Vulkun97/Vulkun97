import time
import pyfirmata
import sys



def shiftOut(data_pin, clock_pin, bit_order, byte_value):
    bited_value = format(byte_value, 'b').zfill(16)
    for i in range(16):
        if bit_order == "LSBFIRST":

            data_pin.write(int(bited_value[15-i]))
        else:
            data_pin.write(int(bited_value[i]))

        clock_pin.write(1)
        clock_pin.write(0)


def setAddress(address, outputEnable):
    if outputEnable:
        shiftOut(shift_data, shift_clk, 'MSBFIRST', (address | 0x0000))
    else:
        shiftOut(shift_data, shift_clk, 'MSBFIRST', (address | 0x8000))
    shift_latch.write(0)
    shift_latch.write(1)
    shift_latch.write(0)

def readEEPROM(address):
    setAddress(address, True)
    for d in eeprom_d:
        d.mode = pyfirmata.INPUT
    time.sleep(0.05)
    return format(int(''.join(['1' if d.read() else '0' for d in eeprom_d]), 2), 'X').zfill(2)

def writeEEPROM(address, data):
    setAddress(address, False)
    for d in eeprom_d:
        d.mode = pyfirmata.OUTPUT
    time.sleep(0.05)
    bin_data = format(int(data, 16), 'b').zfill(8)
    for i, d in enumerate(eeprom_d):
        d.write(int(bin_data[i]))
    write_en.write(0)
    time.sleep(0.001)
    write_en.write(1)
    time.sleep(0.01)

def printContents(bytes_qt):
    print('')
    print('      00 01 02 03 04 05 06 07    08 09 0A 0B 0C 0D 0E 0F', end = '\n\n')
    for line in range(bytes_qt):
        data = list()
        print('{0}:'.format(format(line*16, 'X').zfill(4)), end = ' ')
        for i in range(16*line, 16*(line+1)):
            data.append(readEEPROM(i))
            if i%16 == 7:
                data.append('  ')
        print (*data)


print ('Python pyfirmata EEPROM programmer for Arduino', end = '\n\n')

user_port = input('Enter port name (COM3 is default): ')
user_baud = input('Enter baudrate (9600 is default): ')
port = 'COM3' if user_port == '' else user_port
baudrate = 9600 if user_baud == '' else user_baud
board = pyfirmata.Arduino(port, baudrate = int(baudrate))

shift_data = board.digital[2]
shift_clk = board.digital[3]
shift_latch = board.digital[4]
#eeprom_d = [board.digital[5], board.digital[6], board.digital[7], board.digital[8], board.digital[9], board.digital[10], board.digital[11], board.digital[12]]
eeprom_d = [board.digital[12], board.digital[11], board.digital[10], board.digital[9], board.digital[8], board.digital[7], board.digital[6], board.digital[5]]
write_en = board.digital[13]

time.sleep(1)

it = pyfirmata.util.Iterator(board)
it.start()

write_en.write(1)

while True:
    print('')
    action = input ('Type r to read EEPROM, w to write EEPROM, or x to exit a programm (read is default): ')
    print('')
    if action == 'w':
        bin_filename = input ('Enter bin file name (a.out is default): ')
        try:
            bin_file = open(bin_filename, 'rb')
        except:
            bin_file = open('a.out', 'rb')

        bin_file_contents = bin_file.read(1)
        address = 0
        print ('Programming')
        while len(bin_file_contents) > 0:
            writeEEPROM(address, bin_file_contents.hex())
            bin_file_contents = bin_file.read(1)
            address += 1
        bin_file.close()
        print('')
        print('Done')

    elif action == 'x':
        print ('Bye Bye')
        sys.exit()
    else:
        user_rows = input ('How many rows of 16 bytes do you want to read (default is 4 rows): ')
        rows = 4 if user_rows == '' else user_rows
        printContents(int(rows))
