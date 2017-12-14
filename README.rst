pynetconsole
============

NetConsole (also known as RIOLog) is an insecure protocol used in the FIRST
Robotics Competition to view the output of Robot programs.

Version 2.x only works with RoboRIOs that are imaged for 2018 or beyond. If you
need to talk to a robot imaged prior to 2018, use pynetconsole 1.x instead.

This implementation requires Python 3, and should work on Windows, Linux, and
OSX.

Installation
============

You can easily install this package via pip:

    pip install pynetconsole

Usage
=====

On Windows, you can run netconsole like so::

    py -3 -m netconsole

On OSX/Linux, you can run netconsole like so::

    netconsole

Support
=======

Please file any bugs you may find on our `github issues tracker <https://github.com/robotpy/pynetconsole/issues>`_.

Authors
=======

This implementation of the netconsole listener is derived from the RIOLog
code created by the GradleRIO project.
