import sys
import threading

import pyautogui
import rtmidi
from getkey import getkey, keys


class Main:

    def __init__(self):
        self.n1 = None
        self.n2 = None
        self.dev = rtmidi.RtMidiIn()
        self.mapping = {}
        self.choose_device()
        self.start()
        self.dev.setCallback(self.event_to_key)
        self.main_loop()

    def event_to_key(self, message):
        if message.isNoteOn():
            pyautogui.keyDown(self.mapping.get(message.getNoteNumber(), ''))
        elif message.isNoteOff():
            pyautogui.keyUp(self.mapping.get(message.getNoteNumber(), ''))

    def map_note(self, key):

        def callback(message):
            if message.isNoteOn():
                self.n1 = message.getNoteNumber()
            if message.isNoteOff():
                self.n2 = message.getNoteNumber()
                pyautogui.typewrite('\n')

        self.dev.setCallback(callback)
        input('Play a note to map to the key: ')
        if self.n1 == self.n2:
            self.mapping[self.n1] = key
            print('Note {} mapped to key {}'.format(self.n1, key))
            return True
        print('Please press one note at a time')
        return False

    def choose_device(self):
        print('There are {} devices available:'.format(self.dev.getPortCount()))
        for i in range(self.dev.getPortCount()): print('  {}) {} '.format(i + 1, self.dev.getPortName(i)))
        print()
        while True:
            device = input('Enter a number (default=1): ')
            device = 1 if device == '' else device
            try:
                self.dev.openPort(int(device) - 1)
                break
            except (ValueError, rtmidi.Error):
                print('Invalid value: {}. Please enter an integer between 1 and {}\n'.format(device,
                                                                                             self.dev.getPortCount()))

    def start(self):
        while True:
            print('Press a key to map: ')
            key = keys.name(getkey())
            if key == 'CTRL_D':
                break
            self.map_note(key)

    def main_loop(self):
        while True:
            command = input('Enter a command')


m = Main()


def print_message(midi, port):
    if midi.isNoteOn():
        print('%s: ON: ' % port, midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('%s: OFF:' % port, midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('%s: CONTROLLER' % port, midi.getControllerNumber(), midi.getControllerValue())


class Collector(threading.Thread):
    def __init__(self, device, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            msg = self.device.getMessage()
            if msg:
                print_message(msg, self.portName)


dev = rtmidi.RtMidiIn()
collectors = []
for i in range(dev.getPortCount()):
    device = rtmidi.RtMidiIn()
    device.setCallback(callback)
    device.openPort(i)
    device.ignoreTypes(True, False, True)
    print('OPENING', dev.getPortName(i))
    # collector = Collector(device, i)
    # collector.start()
    # collectors.append(collector)

print('HIT ENTER TO EXIT')
sys.stdin.read(1)
for c in collectors:
    c.quit = True
