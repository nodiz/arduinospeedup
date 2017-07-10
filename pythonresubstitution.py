#!/usr/bin/python
from sys import argv
from os import listdir, path, makedirs, rename
import re
import errno


defines = """#define portOfPin(P)\
(((P)>=0&&(P)<8)?&PORTD:(((P)>7&&(P)<14)?&PORTB:&PORTC))
#define ddrOfPin(P)\
(((P)>=0&&(P)<8)?&DDRD:(((P)>7&&(P)<14)?&DDRB:&DDRC))
#define pinOfPin(P)\
(((P)>=0&&(P)<8)?&PIND:(((P)>7&&(P)<14)?&PINB:&PINC))
#define pinIndex(P)((uint8_t)(P>13?P-14:P&7))
#define pinMask(P)((uint8_t)(1<<pinIndex(P)))

#define pinAsInput(P) *(ddrOfPin(P))&=~pinMask(P)
#define pinAsInputPullUp(P) *(ddrOfPin(P))&=~pinMask(P);digitalHigh(P)
#define pinAsOutput(P) *(ddrOfPin(P))|=pinMask(P)
#define digitalLow(P) *(portOfPin(P))&=~pinMask(P)
#define digitalHigh(P) *(portOfPin(P))|=pinMask(P)
#define isHigh(P)((*(pinOfPin(P))& pinMask(P))>0)
#define isLow(P)((*(pinOfPin(P))& pinMask(P))==0)
#define digitalState(P)((uint8_t)isHigh(P))


"""

fileInput = ""
for filename in listdir('.'):
    if filename.endswith('ino'):
        answ = raw_input("Is %s the sketch you want to edit? y/n: " % (filename))
        if answ.lower() in ["yes","y",""]:
            fileInput = filename
            break
while not path.isfile(fileInput) or not fileInput.endswith('.ino'):
    fileInput = raw_input("Give me your .ino file path, please: ")

path = re.sub(r'(.+\/)(.+)', r'\1', fileInput)
fileOut = re.sub(r'(.+\/)(.+)', r'\1opt\2', fileInput)
bckp_dir = re.sub(r'(.+\/)(.+)', r'\1bckp', fileInput)
bckp_file = re.sub(r'(.+\/)(.+)\.ino', r'\1bckp/\2', fileInput)

try:
    makedirs(bckp_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

out = open(fileOut, "w")
with open(fileInput, 'r') as mod:
    out.write(defines)
    for line in mod.readlines():
        line = re.sub(r'pinMode\((.*)\, INPUT\)', r'pinAsInput(\1)', line)
        line = re.sub(r'pinMode\((.*)\, OUTPUT', r'pinAsOutput(\1', line)
        line = re.sub(r'pinMode\((.*)\, INPUT_PULLUP', r"pinAsInputPullUp(\1", line)
        line = re.sub(r'digitalWrite\((.*)\, LOW', r'digitalLow(\1', line)
        line = re.sub(r'digitalWrite\((.*)\, HIGH', r'digitalHigh(\1', line)
        line = re.sub(r'digitalRead\((.*)\)', r'digitalState(\1)', line)
        out.write(line)

out.close()

rename(fileInput, bckp_file)
rename(fileOut, fileInput)

print("Optimization completed succesfully, backup of your original file store in bckp/ folder")
