#!/usr/bin/env python

#    Episode Renamer GUI
#    
#    Copyright 2010 Torsten Grote
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
from PyQt4 import QtCore, QtGui

from ui_episoderenamer_gui import Ui_MainWindow
import episoderenamer

VERSION = "0.1.0"

class EpisodeRenamerGUI(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		# Icon
		fallbackIcon = QtGui.QIcon()
		if os.path.exists("episoderenamer_gui.svg"):
			fallbackIcon = QtGui.QIcon("episoderenamer_gui.svg")
		self.setWindowIcon(QtGui.QIcon().fromTheme("episoderenamer_gui", fallbackIcon))
		
		# Model
		self.model = QtGui.QStandardItemModel()
		header = QtCore.QStringList("Episode")
		header.append("Renamed Episode")
		self.model.setHorizontalHeaderLabels(header)
		self.ui.file_list.setModel(self.model)
		
		# Connecting signals/actions with slots
		QtCore.QObject.connect(self.ui.addFilesAction, QtCore.SIGNAL("triggered()"), self.file_dialog)
		QtCore.QObject.connect(self.ui.removeFilesAction, QtCore.SIGNAL("triggered()"), self.remove_files)
		QtCore.QObject.connect(self.ui.clearFilesAction, QtCore.SIGNAL("triggered()"), self.clear_files)
		QtCore.QObject.connect(self.ui.previewAction, QtCore.SIGNAL("triggered()"), self.get_new_filenames)
		QtCore.QObject.connect(self.ui.renameFilesAction, QtCore.SIGNAL("triggered()"), self.rename_files)
		QtCore.QObject.connect(self.ui.quitAction, QtCore.SIGNAL("triggered()"), self.close)
		QtCore.QObject.connect(self.ui.modeAction, QtCore.SIGNAL("changed()"), self.switch_mode)
		
		# Shortcuts
		self.ui.removeFilesAction.setShortcuts(QtGui.QKeySequence.Delete)
		self.ui.quitAction.setShortcuts(QtGui.QKeySequence.Quit)

		# Icons
		genericIcon = QtGui.QIcon.fromTheme("document-open")
		self.ui.addFilesAction.setIcon(QtGui.QIcon.fromTheme("list-add", genericIcon)) #folder-new
		self.ui.quitAction.setIcon(QtGui.QIcon.fromTheme("window-close", genericIcon))
		self.ui.removeFilesAction.setIcon(QtGui.QIcon.fromTheme("edit-delete", genericIcon))
		self.ui.clearFilesAction.setIcon(QtGui.QIcon.fromTheme("edit-clear", genericIcon))

		# Context Menu
		self.ui.file_list.addAction(self.ui.addFilesAction)
		self.ui.file_list.addAction(self.ui.removeFilesAction)
		self.ui.file_list.addAction(self.ui.clearFilesAction)
	
		# start in simple mode
		self.switch_mode()
	
		# Connecting drag'n'drop events
		self.ui.file_list.__class__.dragEnterEvent = self.dragEnterEvent
		self.ui.file_list.__class__.dragMoveEvent = self.dragMoveEvent
		self.ui.file_list.__class__.dropEvent = self.dropEvent

	def switch_mode(self):
		if self.ui.modeAction.isChecked():
			self.ui.sourceLabel.show()
			self.ui.sourceComboBox.show()
# unsupported for now
#			self.ui.atomicParsleyLabel.show()
#			self.ui.atomicParsleyCheckBox.show()
			self.ui.maskLabel.show()
			self.ui.maskComboBox.show()
		else:
			self.ui.sourceLabel.hide()
			self.ui.sourceComboBox.hide()
			self.ui.atomicParsleyLabel.hide()
			self.ui.atomicParsleyCheckBox.hide()
			self.ui.maskLabel.hide()
			self.ui.maskComboBox.hide()
	
	
	def file_dialog(self):
		fd = QtGui.QFileDialog(self)
		fd.setFileMode(QtGui.QFileDialog.ExistingFiles)
		filenames = fd.getOpenFileNames()

		from os.path import isfile
		for filename in filenames:
			if isfile(filename):
				self.add_file(filename)


	def add_file(self, filename):			
		episode_item = QtGui.QStandardItem(filename)
		episode_item.setEditable(False)
		renamed_item = QtGui.QStandardItem()
		renamed_item.setEditable(False)
		self.model.appendRow([episode_item,renamed_item])
		self.ui.file_list.resizeColumnToContents(0)
	

	def remove_files(self):
		selected_items = self.ui.file_list.selectionModel().selectedIndexes()
		while len(selected_items):
			self.model.removeRows(selected_items[0].row(), 1)
			selected_items = self.ui.file_list.selectionModel().selectedIndexes()


	def clear_files(self):
		self.model.removeRows(0, self.model.rowCount())


	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
	
	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
			for url in event.mimeData().urls():
				if url.scheme() == "file":
					self.add_file(url.path())


	def get_new_filenames(self):
		show_name = str(self.ui.showLineEdit.text())

		import optparse
		options = optparse.Values
		options.google = True
		options.preview = True
		options.use_atomic_parsley = False

		if self.ui.sourceComboBox.currentText() == 'IMDb API':
			parser = episoderenamer.parse_imdbapi
		elif self.ui.sourceComboBox.currentText() == 'epguides.com':
			parser = episoderenamer.parse_epguides
		else:
			parser = episoderenamer.parse_imdb
		try:
			# Get Show Name
			show = parser(show_name, options)
		except BaseException, e:
			msgBox = QtGui.QMessageBox(self)
			msgBox.setWindowTitle("Episode Renamer - No Show Name")
			msgBox.setIcon(QtGui.QMessageBox.Warning)
			msgBox.setText("The show '%s' could not be found with the current data source engine. Please try a different one." % show_name)
			msgBox.exec_()
			return
		
		# Get List of Files
		files = {}
		for row in range(0,self.model.rowCount()):
			full_filename = str(self.model.item(row).text())
			files[os.path.basename(full_filename)] = full_filename
		
		# Get Mapping from Old Files to New Files
		new_filenames = episoderenamer.rename_files(show, files.keys(), str(self.ui.maskComboBox.currentText()), True, False)
		
		# Update Model with New Files
		for filename in files:
			if filename in new_filenames:
				full_filename = files[filename]
				row = self.model.findItems(full_filename)[0].row()
				self.model.item(row, 1).setText(new_filenames[filename])
		
		self.ui.file_list.resizeColumnToContents(1)
		self.ui.file_list.horizontalScrollBar().setSliderPosition(self.ui.file_list.horizontalScrollBar().maximum())


	def rename_files(self):
		# Display confirmation dialog
		msgBox = QtGui.QMessageBox(self)
		msgBox.setWindowTitle("Episode Renamer - Confirmation")
		msgBox.setIcon(QtGui.QMessageBox.Question)
		msgBox.setText("Are you sure that you want to rename your files as shown?")
		msgBox.setInformativeText("Attention: This can not be undone!")
		msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
		msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
		if msgBox.exec_() == QtGui.QMessageBox.Cancel:
			return
		
		# Rename all files that habe new names
		row_index = []
		for row in range(0,self.model.rowCount()):
			new_file = str(self.model.item(row, 1).text())
			if new_file != "":
				old_filename = str(self.model.item(row, 0).text())
				new_filename = os.path.join(os.path.dirname(old_filename), new_file)
				
				try:
					os.rename(old_filename, new_filename)
					row_index.append(QtCore.QPersistentModelIndex(self.model.index(row, 1)))
				except EnvironmentError, e:
					msgBox = QtGui.QMessageBox(self)
					msgBox.setWindowTitle("Episode Renamer - Renaming Error")
					msgBox.setIcon(QtGui.QMessageBox.Warning)
					msgBox.setText("There was an error renaming '%s': %s" % (old_filename, str(e)))
					msgBox.exec_()
		
		# Delete renamed rows
		for index in row_index:
			self.model.removeRows(index.row(), 1)
		

def main():
	app = QtGui.QApplication(sys.argv)
	ergui = EpisodeRenamerGUI()
	ergui.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
