#!/usr/bin/env python3

from setuptools import setup

setup(
    name="lgsvl",
    description="Python API for SVL Simulator",
    author="LGSVL",
    author_email="contact@svlsimulator.com",
    python_requires=">=3.6.0",
    url="https://github.com/lgsvl/PythonAPI",
    packages=["lgsvl", "lgsvl.dreamview", "lgsvl.evaluator", "lgsvl.wise"],
    install_requires=[
        "websockets==7.0",
        "websocket-client==0.57.0",
        "numpy",
        "environs"
    ],
    license="Other",
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
