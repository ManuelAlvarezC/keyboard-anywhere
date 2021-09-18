# Keyboard Anywhere


This is a fork from the original [Keyboard Anywhere](https://github.com/petermoz/keyboard-anywhere). The installation process is a modified version from this one [Instructables](https://www.instructables.com/Invisible-Piano/).

## Install

This is a summary of the process executed on 2021/03 using `Ubuntu 20.04 LTS`  and `Python 3.9`. We recomend imitate the same environment using `Virtualbox` and a `virtualenv`.


The original installation is done with some dependencies that are not longer available, this is a summary of all the work trying to reproduce it in the forementioned environment.

### System wide requirements

#### OpenKinect

A first introduction to OpenKinect can be fond here. 

Taken from [here](https://openkinect.org/wiki/Getting_Started#Ubuntu_Manual_Install):

```bash
sudo apt-get install git-core cmake libglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev
git clone git://github.com/OpenKinect/libfreenect.git
cd libfreenect
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib64/
cd ..
```

If the process has worked correctly, you should be able to run one of the freenect samples:

```bash
sudo freenect-glview
```

#### Freenect Python builder


```bash
sudo apt-get install cython python-dev python-numpy
cd libfreenect/wrappers/python
```


### Python requirements


sudo add-apt-repository ppa:rock-core/qt4

sudo apt update

sudo apt install libqt4-declarative libqt4* libqtcore4 libqtgui4 libqtwebkit4 qt4*


libqglviewer

http://libqglviewer.com/index.html