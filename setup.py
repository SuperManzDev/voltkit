from setuptools import setup, find_packages

setup(
    name="voltkit",
    version="1.0.0",
    description="VoltKit - Embedded Dev, Hardware & Reverse Engineering Toolkit",
    author="MNZ",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "click>=8.0.0",
        "pyserial>=3.5",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "volt=voltkit.cli:main",
            "voltkit=voltkit.cli:main",
        ],
    },
    python_requires=">=3.8",
)
