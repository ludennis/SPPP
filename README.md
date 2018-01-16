# SPPP
**Self-playing piano parser**

## Instructions
* copy and paste parser.py into the directory that contains your midi file
* use "dir" and "cd" to traverse into the directory
* call python parser.py [input_file_name] (ex C:\python27\python.exe parser.py what-made-you-die.txt)
* a python file named input_file_name.py will be created

## Commands for 'parser.py'
* ```shell"parser.py [input_text]``` (e.g. ```shell parser.py input.txt```)
* ```shell parser.py -t [start_key] [end_key] [min_pwr] [max_pwr] [inc_pwr]``` (e.g. ```shell parser.py -t 24 96 60 100 5```)
* ```shell parser.py -t [start_key] [end_key] [pwr]``` (e.g. ```shell parser.py -t 24 96 70```)
* ```shell parser.py -h``` (shows the list of commands and their parameters)
* ```shell parser.py [input_text] --tmin=[target_min] --tmax=[target_max]``` (e.g. ```shell parser.py departures.txt --tmin=105 --tmax=180```)
	note: default value is `--tmin=105` and `--tmax=180` if you don't specify

## TODO's
- [] add version
- [] to read straight from midi file

