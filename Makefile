all:
	pyuic4 episoderenamer_gui.ui -o ui_episoderenamer_gui.py -i 0
	pyuic4 episoderenamer_gui_about.ui -o ui_about.py -i 0

clean:
	rm ui_episoderenamer_gui.py
	rm ui_about.py
	rm *.pyc
