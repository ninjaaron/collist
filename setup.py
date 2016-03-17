from setuptools import setup

setup(
    name='collist',
    version='0.1',
    py_modules=['collist'],
    entry_points={'console_scripts': ['cols=collist:main']},
    )
