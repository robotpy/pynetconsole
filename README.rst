pynetconsole
============

NetConsole is an insecure protocol used in the FIRST Robotics Competition to
view the output of Robot programs.

On the cRIO platform, netconsole provides a console interface to vxWorks, with
input and output support.

On the roboRIO platform, this provides access to output only when your program
is ran using netconsole-host (which is done automatically for you by the
C++/Java/python deployment tools).

This implementation has been tested on Python 2 and 3, and should work on
Windows, Linux, and OSX.

Installation
============

You can easily install this package via pip:

    pip install pynetconsole

Usage
=====

On Windows, you can run netconsole like so::

    py -m netconsole

On OSX/Linux, you can run netconsole like so::

    netconsole

Support
=======

Please file any bugs you may find on our `github issues tracker <https://github.com/robotpy/pynetconsole/issues>`_.

Authors
=======

This implementation of the netconsole listener was originally written by
Robert Blair Mason Jr.

It has since been maintained and enhanced by the RobotPy project.
