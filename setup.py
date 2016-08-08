from setuptools import setup

try:
    from urllib import request
except ImportError:
    import urllib2 as request

fastep = request.urlopen('https://raw.githubusercontent.com/ninjaaron/fast-entry_points/master/fastentrypoints.py')
namespace = {}
exec(fastep.read(), namespace)

setup(
    name='collist',
    version='0.5',
    py_modules=['collist'],
    install_requires=['click'],
    long_description=open('README.rst').read(),
    url='https://github.com/ninjaaron/collist',
    author='Aaron Christianson',
    author_email='ninjaaron@gmail.com',
    license='MIT',
    entry_points={'console_scripts': ['cols=collist:main']},
    )
