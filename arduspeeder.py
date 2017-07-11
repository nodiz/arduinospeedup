import os
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
for filename in os.listdir('.'):
    if filename.endswith('ino'):
        answ = raw_input("Is %s the sketch you want to edit? y/n: " % (filename))
        if answ.lower() in ["yes", "y", ""]:
            fileInput = filename
            break
while not os.path.isfile(fileInput) or not fileInput.endswith('.ino'):
    fileInput = raw_input("Give me your .ino file path, please: ")

path = re.sub(r'(.+\/)(.+)', r'\1', fileInput)
fileOut = re.sub(r'(.+\/)(.+)', r'\1opt\2', fileInput)
bckp_dir = re.sub(r'(.+\/)(.+)', r'\1bckp', fileInput)
bckp_file = re.sub(r'(.+\/)(.+)\.ino', r'\1bckp/\2', fileInput)

try:
    os.makedirs(bckp_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

out = open(fileOut, "w")
with open(fileInput, 'r') as mod:
    out.write(defines)
    for line in mod.readlines():

        line = re.sub(r'pinMode\(\s*(.*)\s*,\s*INPUT\)', r'pinAsInput(\1)', line)
        line = re.sub(r'pinMode\(\s*(.*)\s*,\s*OUTPUT', r'pinAsOutput(\1', line)
        line = re.sub(r'pinMode\(\s*(.*)\s*,\s*INPUT_PULLUP', r"pinAsInputPullUp(\1", line)
        line = re.sub(r'digitalRead\(\s*(.*)\)', r'digitalState(\1)', line)

        line = re.sub(r'digitalWrite\((.*)\s*,\s*LOW', r'digitalLow(\1', line)
        line = re.sub(r'digitalWrite\(\s*(.*)\s*,\s*HIGH', r'digitalHigh(\1', line)
        line = re.sub(r'digitalWrite\((.*)\s*,\s*0', r'digitalLow(\1', line)
        line = re.sub(r'digitalWrite\(\s*(.*)\s*,\s*1', r'digitalHigh(\1', line)

        line = re.sub(r'digitalState\((.*)\)\s*==\s*HIGH\s*', r'isHigh(\1)', line)
        line = re.sub(r'digitalState\((.*)\)\s*==\s*LOW\s*', r'isLow(\1)', line)
        line = re.sub(r'digitalState\((.*)\)\s*==\s*1\s*', r'isHigh(\1)', line)
        line = re.sub(r'digitalState\((.*)\)\s*==\s*0\s*', r'isLow(\1)', line)

        out.write(line)
out.close()

os.rename(fileInput, bckp_file)
os.rename(fileOut, fileInput)

print "Optimization completed succesfully, backup of your original file stored in bckp/ folder"
