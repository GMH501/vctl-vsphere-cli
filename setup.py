from setuptools import setup

setup(
    name="vctl",
    version="0.1",
    author="Gabriel Meghnagi",
    author_email="gabrielmeghnagi@outlook.it",
    py_modules=["vctl"],
    include_package_data=True,
    install_requires=["click", "pyyaml", "pyvmomi", "pyvim"],
    entry_points="""
        [console_scripts]
        vctl=vctl:cli
    """,
    )