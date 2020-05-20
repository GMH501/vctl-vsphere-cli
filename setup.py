from setuptools import setup

setup(
    name="vctl",
    version="0.1",
    author="Gabriel Meghnagi",
    author_email="gabrielmeghnagi@outlook.it",
    description="An unofficial API based command line utility for inspecting one or more vSphere environments.",
    url="https://github.com/GMH501/vctl-sphere-cli",
    py_modules=["vctl"],
    include_package_data=True,
    install_requires=["click", "pyyaml", "pyvmomi", "pyvim"],
    entry_points="""
        [console_scripts]
        vctl=vctl:vctl
    """,
    )
