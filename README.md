![Alt text](./images/icon.png?raw=true)
# gr-pus
The gr-pus OOT package incorporates the Packet Utilization Services ECSS-E-ST-70-41C interfaces and services into GNURadio.
 
Additional ad-hoc (application specific) services could easily be added later as OOT blocks.

The folder docs includes a document with the description and the user manual, in addicion there is a sheet document with QA test cases tracking

This implementation is based in the AcubaSat one (https://github.com/AcubeSAT/ecss-services), but adapted to GNURadio and including full verification support, additional service types and message types. 


![Alt text](./images/schematic.png?raw=true "gr-pus schematic")

Because this package is for GNURadio and Linux, it is not intented to be a "flight software" as so. The "Flight software", as any critical softare, has a set of specific requirements, but, those requirements have a clear objetive, and knowing the risks you could deviate them.

I found out that for certain cases where the risk is very low, it is far better to use Linux as O/S in a SoC instead of RTEMS (which, by the way, the v3.10+ is not a "flight software" neither!) or Vxworks, Linux will simplified (time, money, etc) the development and testing process (no special tools, simulators, knowledge is required!). 

gr-pus is aimed to such cases (ie: SDR instruments)!


## Installation

GNURadio 3.10 is required for this installation

Install the Embed Template Library:

```
git clone https://github.com/ETLCPP/etl.git
cd etl
git checkout <targetVersion>
cmake -B build .
sudo cmake --install build/
```

Install pySerial for the serial port block helper
```
pip3 install pyserial
```
or
```
sudo apt-get update -y
sudo apt install python3-serial
```
Install nlohmann for json parsing:
```
sudo apt-get update –y
sudo apt-get install -y nlohmann-json-dev
```
Then install gr-pus:
```
git clone https://github.com/gjg/gr-pus.git
cd gr-pus
mkdir build 
cd build
cmake ..
make
sudo make install
sudo ldconfig
```
