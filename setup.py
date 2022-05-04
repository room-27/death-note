from setuptools import setup, find_packages


setup(
    name='death-note',
    version='0.1',
    packages=find_packages(),
    url='http://github.com/room-27/death-note',
    license='MIT',
    author='Dylan Risso',
    author_email='room27projects@gmail.com',
    description='Temporary',
    install_requires=[

    ],
    entry_points={
        'console_scripts': [
            'deathnote = src.main:main'
        ]
    }
)