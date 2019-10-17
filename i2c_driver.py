"""
Modified Python I2C library for Raspberry Pi
By:DenisFromHR (Denis Pleic) -- 10/02/2015, ver 0.1
Updated: Lemon65 -- 10/16/2019
"""
import smbus, logging
from time import *

logger = logging.getLogger('RPLCD')

# LCD line Range
LCD_MIN_LINE = 1
LCD_MAX_LINE = 4

# LCD CHAR Range
LCD_MIN_CHAR = 0
LCD_MAX_CHAR = 19

# LCD Address
ADDRESS = 0x27

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class i2c_device:
   def __init__(self, addr, port=1):
      """init call to the i2c_device Class
      Arguments:
          addr {[int]} -- address for the LCD
      
      Keyword Arguments:
          port {int} -- port number for the LCD (default: {1})
      """
      self.addr = addr
      self.bus = smbus.SMBus(port)

   def write_cmd(self, cmd):
      """ Write a single command
      
      Arguments:
          cmd {[Hex/Byte]} -- Command call, defined in the globals
      """
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

   def write_cmd_arg(self, cmd, data):
      """ Write a command and argument"""
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)

   def write_block_data(self, cmd, data):
      """ Write a block of data """
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)

   def read(self):
      """ Read a single byte from the I2C LCD Bus """
      return self.bus.read_byte(self.addr)

   def read_data(self, cmd):
      """ Read byte's from the I2C LCD Bus """
      return self.bus.read_byte_data(self.addr, cmd)

   def read_block_data(self, cmd):
      """ Read a block of data from the I2C LCD Bus"""
      return self.bus.read_block_data(self.addr, cmd)

class RPLCD:
   def __init__(self):
      """ initializes objects and lcd for the RPLCD Class """
      self.lcd_device = i2c_device(ADDRESS)

      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x02)

      self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
      self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
      self.lcd_write(LCD_CLEARDISPLAY)
      self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
      sleep(0.2)

   def lcd_strobe(self, data):
      """ clocks EN to latch command """
      self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
      sleep(.0005)
      self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
      sleep(.0001)

   def lcd_write_four_bits(self, data):
      """ Commands the LCD to Write four bits of data to the LCD """
      self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
      self.lcd_strobe(data)

   def lcd_write(self, cmd, mode=0):
      """ Writes strings to the LCD, as well as its used to send commands (see globals)
      
      Arguments:
          cmd {[Hex/Byte]} -- Command call, defined in the globals
      
      Keyword Arguments:
          mode {int} --  Register Setting info -- (default: {0})
      """
      self.lcd_write_four_bits(mode | (cmd & 0xF0))
      self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

   def lcd_clear(self):
      """ Clears the LCD and commands the cursor home (0, 0), uses lcd_write() """
      self.lcd_write(LCD_CLEARDISPLAY)
      self.lcd_write(LCD_RETURNHOME)

   def backlight(self, state):
      """ Function to set the backlight on/off
      Arguments:
          state {[int]} -- State to turn on and off the backlight - 1=ON, 0=OFF
      """
      if state == 1:
         self.lcd_device.write_cmd(LCD_BACKLIGHT)
      elif state == 0:
         self.lcd_device.write_cmd(LCD_NOBACKLIGHT)
        
   def lcd_display_string(self, string_data, line):
      """This function writes data to the LCD, taking a string under 20 characters and
      the line you want to write to.
      
      Arguments:
          string_data {[str]} -- string data to write to the LCD (under 20 CHARS)
          line {[int]} -- This is the line that you are writing to Line Range: [1,2,3,4]
      """
      if line == 1:
         self.lcd_write(0x80)
      if line == 2:
         self.lcd_write(0xC0)
      if line == 3:
         self.lcd_write(0x94)
      if line == 4:
         self.lcd_write(0xD4)
      for char in string_data:
         self.lcd_write(ord(char), Rs)
   
   def lcd_display_string_pos(self, string_data, line, position):
      """ Define precise positioning when displaying text on the LCD
      Arguments:
          string_data {[str]} -- string data to write to the LCD (under 20 CHARS)
          line {[int]} -- target line you want to write your data to -- [1, 2, 3, 4]
          position {[int]} -- position on that line you want to start writing [0, 19]
                                 Note -- this position value starts at 0
      """
      if line not in range(LCD_MIN_LINE, LCD_MAX_LINE):
         logger.error("The Input line: %s, is out of Range --> [%s - %s]" % (line, LCD_MIN_LINE, LCD_MAX_LINE))
         return
      if position not in range(LCD_MIN_CHAR, LCD_MAX_CHAR):
         logger.error("The position: %s, is out of Range --> [%s - %s]" % (line, LCD_MIN_CHAR, LCD_MAX_CHAR))
         return
      if line == 1:
         position_new = position
      if line == 2:
         position_new = 0x40 + position
      if line == 3:
         position_new = 0x14 + position
      if line == 4:
         position_new = 0x54 + position
         
      self.lcd_write(0x80 + position_new)
      for char in string_data:
         self.lcd_write(ord(char), Rs)
