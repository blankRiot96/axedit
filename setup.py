from pathlib import Path

from setuptools import find_packages, setup

VERSION = "0.1.2"
DESCRIPTION = "Modal Text Editor"
LONG_DESCRIPTION = """Axedit is a light, fast and aesthetic modal editor for Python. 
Attempts to implement vim-like motions."""

setup(
    name="axedit",
    version=VERSION,
    author="Axis (blankRiot96)",
    email="blankRiot96@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "pygame-ce",
        "tomlkit",
        "jedi",
        "colorama",
        "PyYAML",
        "rapidfuzz",
        "clipboard",
    ],
    python_requires=">=3.11",
    keywords=["editor"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Editors",
        "Intended Audience :: Developers",
    ],
    entry_points={"console_scripts": ["axedit=axedit:main", "axe=axedit:main"]},
    include_package_data=True,
    data_files=[str(p) for p in Path("axedit/assets/").rglob("*") if not p.is_dir()],
)
