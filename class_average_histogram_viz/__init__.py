"""Web application to visualize particle count distributions of distinct views from a set of class averages"""

# Add imports here
from .interactive_dash_plot import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
