UI_File=episoderenamer_gui.ui
Output_File=ui_episoderenamer_gui.py

all:
	pyuic4 ${UI_File} > ${Output_File}

clean:
	rm ${Output_File}
	rm *.pyc
