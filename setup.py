from setuptools import setup

setup(
    name='collist',
    version='0.2',
    py_modules=['collist'],
    install_requires=['click'],
    long_description=open('README.rst').read(),
    url='https://github.com/ninjaaron/collist',
    author='Aaron Christianson',
    author_email='ninjaaron@gmail.com',
    license='MIT',
    entry_points={'console_scripts': ['cols=collist:main']},
    )



