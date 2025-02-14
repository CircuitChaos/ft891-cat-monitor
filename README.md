# CAT meters monitor for Yaesu FT-891

This is a simple command-line Python script that displays values of various meters of the Yaesu FT-891 in real time:

* RX: Signal level (dB, S)
* TX: ALC level (%)
* TX: Measured TX power level (W)
* TX: VSWR
* TX: Current of final transistors (amps)

Script was developed and tested on Linux. Should probably work also on Windows if you set the port correctly.

## Usage

You need `python3` and `serial` module to run this script.

Set the port and baudrate in the script (or keep the port and see my udev rules below). Optionally adjust the polling interval as well (by default it's set to 250 ms). Run without arguments and it should work.

If it can't find the serial module (`ModuleNotFoundError: No module named 'serial'`), you need to install this module. On Debian, simply run: `apt-get install python3-serial`. On other systems use the appropriate package, or try `pip3 install serial`.

## Example output

In RX:

```
RX Sig:    83 [#####           ] S6 (-16 dB)
```

In TX:

```
TX ALC:   109 [######          ] 85%
TX Power: 207 [############    ] 98.7 W
TX SWR:    13 [                ] 1.13
TX Idd:   115 [#######         ] 13.5 A
```

You can see the meter name, raw value (from 0 to 255), graphical representation, and a more meaningful value, calculated from the raw one using calibration tables embedded in the script.

## What about the compressor level?

One other meter that FT-891 provides is the compressor level. I don't need it, so I didn't implement it. It's trivial to add it, but it needs to be calibrated. If you need it, feel free to add and calibrate it and create PR.

## Calibration

Radio returns meter values as raw, uncalibrated values in range 0...255. I did my best to calibrate them, but I can't guarantee the correctness. Don't rely on it (use your brain at all times). If something seems off, let me know.

## Limitations

Obviously, you can't use CAT interface while this program is running, but you can use DTR / RTS on another serial port (the radio provides two serial ports via the USB connection, one is for CAT and one is for PTT) to key it. I used it successfully with WSJT-X keying the transceiver this way.

The tool was developed for FT-891, and won't run if it detects another model. You're free to experiment if you have another radio model, just know that calibration might be completely off.

## udev rules

Here are some useful udev rules that I use to make sure that:

* my CAT port is always /dev/ttyFTCAT
* my PTT port is always /dev/ttyFTPTT

```
# FT-891 CAT port
ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea70", ENV{ID_USB_INTERFACE_NUM}=="00", SUBSYSTEM=="tty", SYMLINK+="ttyFTCAT"

# FT-891 PTT port
ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea70", ENV{ID_USB_INTERFACE_NUM}=="01", SUBSYSTEM=="tty", SYMLINK+="ttyFTPTT"
```

Another useful rule to make the sound card used to communicate with FT-891 always have the same name: 
See here: https://www.alsa-project.org/wiki/Changing_card_IDs_with_udev

## License

Public domain. Do what you want with it. Just use it at your own risk and don't hold me accountable if your rig or PC explodes.

## Contact with author

Please use GitHub issue tracker or email: circuitchaos (at) interia.com
