#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "color_grouper",
    version='0.0.1',
    package_dir={"": "src"},
    packages=["color_grouper"],
    entry_points={
        "console_scripts": [
            "reader = color_grouper.reader:main",
            "generator = color_grouper.generator:main",
            "sorter = color_grouper.sorter:main",
        ],
    },
)