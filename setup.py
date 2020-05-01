from setuptools import setup

setup(
    name="vcli",
    version="0.1",
    author="Gabriel Meghnagi",
    author_email="gabrielmeghnagi@outlook.it",
    py_modules=["vc"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        vc=vc:cli
    """,
    )