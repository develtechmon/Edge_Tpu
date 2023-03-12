# Gstreamer installation guide on RPI 4 

## Introduction
In this userguide, i'm going to show how to install Gstreamer in RPi that should cover below version

* `Bullseye`
* `Buster` (For installation refer to below link)

Read this [link](https://qengineering.eu/install-gstreamer-1.18-on-raspberry-pi-4.html) first and use it as a reference alongside


## Installation 
Check `gstreamer` version using below command to check if `1.18.4-2.1` is installed.
```
dpkg -l | grep gstream
```

Install below plugins
```
# install a missing dependency
$ sudo apt-get install libx264-dev libjpeg-dev
# install the remaining plugins
$ sudo apt-get install libgstreamer1.0-dev \
     libgstreamer-plugins-base1.0-dev \
     libgstreamer-plugins-bad1.0-dev \
     gstreamer1.0-plugins-ugly \
     gstreamer1.0-tools \
     gstreamer1.0-gl \
     gstreamer1.0-gtk3
# if you have Qt5 install this plugin
$ sudo apt-get install gstreamer1.0-qt5
```

## Streaming
With all Gstreamer modules installed, let's test the installation with below command
```
gst-launch-1.0 videotestsrc ! videoconvert ! autovideosink
```

The major differences between `Buster` and `Bullseye` is the camera source. 

Buster - you could call
```
v4l2src device=/dev/video0` or `rpicamsrc
```

Bullseye - you could call
```
libcamerasrc
```

For example as follow
```
gst-launch-1.0 libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! videoscale ! clockoverlay time-format="%D %H:%M:%S" ! autovideosink
```
