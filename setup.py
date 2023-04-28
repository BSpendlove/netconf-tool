from setuptools import setup, find_packages


setup(
    name="netconf_tool",
    version="0.0.1",
    packages=find_packages(exclude=("dev")),
    include_package_data=True,
    install_requires=[
        "ncclient>=0.6.13",
        "loguru>=0.7.0",
        "click>=8.1.3",
        "click-plugins>=1.1.1",
    ],
    entry_points="""
        [console_scripts]
        netconf-tool=netconf_tool.cli:cli
    """,
)
