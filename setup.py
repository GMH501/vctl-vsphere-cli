from setuptools import setup

setup(
    name="vc-vcenter-cli",
    version="0.1",
    author="Gabriel Meghnagi"
    py_modules=["vc"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        vc=vc:cli
    """,
    )
