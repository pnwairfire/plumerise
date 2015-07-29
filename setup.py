from setuptools import setup, find_packages

from plumerise import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='plumerise',
    version=__version__,
    license='MIT',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[],
    package_data={
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/plumerise',
    description='Package for computing plume rise from emissions output.',
    install_requires=[
        "pyairfire>=0.8.16"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/",
    ],
    tests_require=test_requirements
)
