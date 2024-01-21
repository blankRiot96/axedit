from setuptools import find_packages, setup

VERSION = "0.1.0"
DESCRIPTION = "Modal Editor"
LONG_DESCRIPTION = """Modal text editor"""

# Setup
setup(
    name="axedit",
    version=VERSION,
    author="Axis (blankRiot96)",
    email="blankRiot96@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["pygame-ce"],
    python_requires=">=3.11",
    keywords=["editor"],
    # classifiers=[
    #     "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    #     "Programming Language :: Python :: 3.7",
    #     "Programming Language :: Python :: 3.8",
    #     "Programming Language :: Python :: 3.9",
    #     "Programming Language :: Python :: 3.10",
    #     "Topic :: Artistic Software",
    #     "Topic :: Multimedia :: Sound/Audio",
    #     "Intended Audience :: End Users/Desktop",
    # ],
    entry_points={"console_scripts": ["axedit=axedit:main", "axe=axedit:main"]},
)
