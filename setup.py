#!/usr/bin/env python

from setuptools import setup
from episoderenamer_gui import VERSION

setup(name='episoderenamer-gui',
	version=VERSION,
	description='TV episodes renamer',
	long_description='Renames episodes of TV shows with proper names',
	
	author='Torsten Grote',
	author_email='Torsten.Grote@fsfe.org',
	url='http://github.com/Tovok7/episode-renamer-gui',
	license = "GPLv3+",
	classifiers=[
		'Programming Language :: Python',
		'Topic :: Multimedia :: Video',
	],

	scripts=['episoderenamer_gui.py'],
	py_modules = ['ui_episoderenamer_gui'],
	data_files=[
		('share/icons/hicolor/scalable/apps', ['episoderenamer_gui.svg']),
		('share/applications', ['episoderenamer_gui.desktop'])
	],
	install_requires=["episode-renamer>=0.4.5"],
	entry_points = {
		'gui_scripts': ['episoderenamer-gui = episoderenamer_gui:main']
	}
)
