#!/usr/bin/env python
try:
    from setuptools import setup 
except ImportError, err:
    from distutils.core import setup

from sharrock import VERSION

setup(
    name='Sharrock',
    version='.'.join(map(str,VERSION)),
    description='Python remote procedure call framework with server and client components.  RESTful when you need it to be.',
    packages=['sharrock'],
    include_package_data=True,
    license='BSD',
    author='Loren Davie',
    author_email='code@axilent.com',
    url='https://github.com/Axilent/sharrock',
    install_requires=['requests','Django>=1.4','Markdown==2.0.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)