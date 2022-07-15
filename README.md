# irmagician

IRMagician Operation Tool

## Usage

```shell
sudo chmod 666 /dev/ttyACM0 # for Linux
sudo chmod 666 /dev/cu.usbmodem01231 # for MacOS

# 1. Recode
python irmagician.py -c 

# 2. Playback
python irmagician.py -p

# 3. Save
python irmagician.py -s -f /path/to/filename.json

# 4. Reproduction
python irmagician.py -p -f /path/to/filename.json
```
