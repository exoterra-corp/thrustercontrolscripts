# intro
This is the halo8 scripts driver.  The goal of these modules is to make it really easy to write a script to interact with the ppu, and only at most 2 layers of abstractions.  So its easy to see how everything works together.

# Organization
The driver is split into 2 layers a base communication layer and a driver helper layer.  The driver layer use is optional and examples below will show how just the comms layer alone can be used to communicate with the ppu.  If more features and abstractions are wanted they can be added in with minimal changes, and will also be shown below.

File List:
- _console_tui.py - The internal gui that can be used in the terminal to show more information in a script.  Best show in use in thruster_command.py
- comms.py - This base layer level Comms class, this class can be used standalone to communicate with the ppu.  It is also integrated with the PPU class for use as well.
- console.py - This class  
- defines.py - Hold the canopen index and subindex defines used by the scripts, also holds the hsi structure for parsing.
- exceptions.py - Custom exceptions for the base level classes.
- listener.py - Higher level class that can listen and show raw serial packets, telemetry packets, and or trace messages. 
- mr_logger.py - Custom logger that can be used in each script. It can handle saving everything talked about above as well as a sys line.  Everything timestamped in logged in a file.
- ppu.py - Base PPU class to be used in a script to make everything available and easy to use.
- state.py - Gathers and sets state of the ppu, nmt, thruster statue and telemetry messages.
- telem_window.py - the gui side of the listener script, small flask app that displays all of the hsi in a browser window.
- update.py - PPU updated broken out into a class for use in a script.
- version.py - Versions broken out into a class for use in a script.

# Examples of comms standalone


# Example of Full ppu class override