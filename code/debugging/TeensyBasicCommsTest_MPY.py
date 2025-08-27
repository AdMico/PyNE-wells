import serial

ser = serial.Serial(
    port="/dev/ttyACM0",  # Change this to your Teensy's port
    baudrate=9600, # Or your configured baudrate
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1 # Timeout in seconds
)

flag = True
def tell(msg):
    msg = msg + "\n"
    x = msg.encode("ascii") # encode n send
    ser.write(x)

def hear():
    msg = ser.read_until() # read until a new line
#    msg = ser.read()
    mystring = msg.decode("ascii")  # decode n return
#    mystring = msg
    return mystring

while flag == True:
    val = input() # take user input
    if (val == "exit"):
        flag = False
    tell(val) # send it to arduino
    var = hear() # listen to arduino
    print(var) #print what arduino sent

