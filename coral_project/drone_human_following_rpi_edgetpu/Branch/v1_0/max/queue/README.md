# Getting Started

## Run using SiTL

To establish SiTL connection we're going to use
```
Gazebo (For Drone in 3D space dimension) or Cygwin
```

## Gazebo
From Ubuntu Desktop launch Gazebo using below command
```
gazebo --verbose ~/ardupilot_gazebo/worlds/iris_arducopter_runway.world
```

Run below command to establish `SITL` command to accept the connection from RPI address to Gazebo
```
cd ~/ardupilot/ArduCopter/

sim_vehicle.py -v ArduCopter -f gazebo-iris --console --out 192.168.195.204:14553

Note : "192.168.195.204:14553" is referring to JetsonNano or RPI address of our drone
```

## Cygwin
Alternatively, can use Cygwin. To launch Cygwin run below command
```
../Tools/autotest/sim_vehicle.py --console --map --out 192.168.195.204:14553

Note : "192.168.195.204:14553" is referring to JetsonNano or RPI address of our drone
```

From RPI, run `connect_drone.py` to test the connection. Before run, please use below `connection_string` which is referring to RPI IP address
```
connection_string = '192.168.195.204:14553'
```
## Run using Pixhawk

Please ensure correct wire connection to RPI and Pixhawk UART. See connection
configuration below and Mission Planner Setting to enable the communication

```
Hardware Setting
RPI     Pixhawk
Tx  ---   Rx
Rx  ---   Tx
Gnd ---   Gnd

Mission Planner
Telemetry 2 (Serial 2)
SERIAL2_BAUD = 921600
SERIAL2_PROTOCOL = 1 (Mavlink)
```

Run `mavproxy` command below to test the communication between RPI and Pixhawk
```
mavproxy.py --master=/dev/ttyAMA0,921600
```

You can also, run `connect_drone.py` to test the connection. Before run, please use below `connection_string` which is referring to RPI IP UART Port
```
connection_string = '/dev/ttyAMA0,921600'
```

# Install as a service to run after boot
```
$ crontab -e

Add following line
@reboot echo 2328 | /usr/bin/python3 /home/jlukas/Desktop/My_Project/Edge_Tpu/coral_project/drone_human_following_rpi_edgetpu/main.py

Run below command to ensure our service installed successfully
$ crontab -l

```