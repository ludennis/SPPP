# SPPP
**Self-playing piano parser**

## Instructions
* copy and paste parser.py into the directory that contains your midi file
* use "dir" and "cd" to traverse into the directory
* call python parser.py [input_file_name] (ex C:\python27\python.exe parser.py what-made-you-die.txt)
* a python file named input_file_name.py will be created

## Commands for 'parser.py'

* `parser.py [input_text]` (e.g. `parser.py input.txt`)
* `parser.py -t [start_key] [end_key] [min_pwr] [max_pwr] [inc_pwr]` (e.g. `parser.py -t 24 86 100 20 100 20`)
* `parser.py -t [start_key] [end_key] [pwr]` (e.g. `parser.py -t 24 96 70`)
* `parser.py -h` (shows the list of commands and their parameters)
* `parser.py [input_text] --tmin=[target_min] --tmax=[target_max]` (e.g. `parser.py departures.txt --tmin=105 --tmax=180`)
	note: default value is `--tmin=105` and `--tmax=180` if you don't specify

## Using Profiles for Individual Keys
example:
* `parser.py midi/test.txt -profile 'profiles'`

## TODO's
- [ ] add version
- [ ] to read straight from midi file

