# SPPP
Self-playing piano parser

Instructions
1. copy and paste parser.py into the directory that contains your midi file
2. use "dir" and "cd" to traverse into the directory
2. call python parser.py [input_file_name] (ex C:\python27\python.exe parser.py what-made-you-die.txt)
3. a python file named input_file_name.py will be created

Commands for 'parser.py'
1. "parser.py [input_text]" (e.g. "parser.py input.txt")
2. "parser.py -t [start_key] [end_key] [min_pwr] [max_pwr] [inc_pwr]" (e.g. "parser.py -t 24 96 60 100 5")
3. "parser.py -t [start_key] [end_key] [pwr]" (e.g. "parser.py -t 24 96 70")
4. "parser.py -h" 
5. "parser.py --target-average=[target_average_power]" (e.g. "parser.py departures.txt --target-average=50")

TODO's
1. to have desired max, min, and average power level
