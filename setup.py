import os
import runpy
from setuptools import setup, find_packages

# Get version
cwd = os.path.abspath(os.path.dirname(__file__))
versionpath = os.path.join(cwd, 'zdsim', 'version.py')
version = runpy.run_path(versionpath)['__version__']

# # Get the documentation
# with open(os.path.join(cwd, 'README.rst'), "r") as f:
long_description = (
    "zdsim, an agent-based model of zero-dose vaccination and pentavalent "
    "disease burden among under-five children, implemented using the "
    "Starsim framework (>=3.3.2)."
)


setup(
    name="zdsim",
    version=version,
    author="Minerva Enriquez, Robyn Stuart, Cliff Kerr, Romesh Abeysuriya, Paula Sanz-Leon, Jamie Cohen, and Daniel Klein on behalf of the zdsim Collective",
    description="zdsim",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords=["agent-based model", "simulation", "disease", "epidemiology"],
    platforms=["OS Independent"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "starsim>=3.3.2",
        "sciris>=3.0",
        "openpyxl>=3.0",
        "reportlab>=4.0",
    ],
    extras_require={
        "test": ["pytest"],
    },
)
