#!/usr/bin/env python
#
# Script to sort the game controller database entries in SDL_gamecontroller.c

import re


filename = "SDL_gamecontrollerdb.h"
input = open(filename)
output = open(f"{filename}.new", "w")
parsing_controllers = False
controllers = []
controller_guids = {}
split_pattern = re.compile(r'([^"]*")([^,]*,)([^,]*,)([^"]*)(".*)')

def save_controller(line):
    global controllers
    match = split_pattern.match(line)
    entry = [ match.group(1), match.group(2), match.group(3) ]
    bindings = sorted(match.group(4).split(","))
    if (bindings[0] == ""):
        bindings.pop(0)
    entry.extend(",".join(bindings) + ",")
    entry.append(match.group(5))
    controllers.append(entry)

def write_controllers():
    global controllers
    global controller_guids
    for entry in sorted(controllers, key=lambda entry: entry[2]):
        line = "".join(entry) + "\n"
        if not line.endswith(",\n") and not line.endswith("*/\n"):
            print(f"Warning: '{line}' is missing a comma at the end of the line")
        if (entry[1] in controller_guids):
            print(
                f"Warning: entry '{entry[2]}' is duplicate of entry '{controller_guids[entry[1]][2]}'"
            )
        controller_guids[entry[1]] = entry

        output.write(line)
    controllers = []
    controller_guids = {}

for line in input:
    if parsing_controllers:
        if (line.startswith("{")):
            output.write(line)
        elif (line.startswith("    NULL")):
            parsing_controllers = False
            write_controllers()
            output.write(line)
        elif (line.startswith("#if")):
            print(f"Parsing {line.strip()}")
            output.write(line)
        elif (line.startswith("#endif")):
            write_controllers()
            output.write(line)
        else:
            save_controller(line)
    else:
        if (line.startswith("static const char *s_ControllerMappings")):
            parsing_controllers = True

        output.write(line)

output.close()
print(f"Finished writing {filename}.new")
