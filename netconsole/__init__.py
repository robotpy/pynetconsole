try:
    from .version import __version__
except ImportError:
    __version__ = "master"

from .netconsole import Netconsole, run
