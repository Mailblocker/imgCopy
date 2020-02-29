'''
Created on 05.12.2018

@author: Mailblocker
'''

import sys
import argparse
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QSize
from PyQt5.Qt import QPushButton, QFileDialog, QFileInfo, QTextEdit, QThread,\
    pyqtSignal
from shutil import copyfile
import os
import glob

class copyThread(QThread):
    newText = pyqtSignal(str)
    
    def __init__(self, source = '', destination = ''):
        QThread.__init__(self)
        self.sourcePath = source
        self.destinationPath = destination
        
    def run(self):
        file = QFileInfo(self.sourcePath)
            
        lines = [file.path() + '/' + line.rstrip('\n') for line in open(file.absoluteFilePath())]
        self.newText.emit('--------------------------------------------------------------------------------')
        self.newText.emit('Now copying {} files.'.format(len(lines)))
    
        count = 1
        for x in lines:
            if QFileInfo(x).exists():
                y = self.destinationPath + '/IMG_' + "{:04}".format(count) + '.' + QFileInfo(x).suffix()
                self.newText.emit('copying {} to {}'.format(x, y))
                copyfile(x, y)
                count = count + 1
            else:
                mList = glob.glob(file.path() + '/**/' + os.path.basename(x), recursive=True)
                if 1 == len(mList):
                    # Found 1 file we will use this one
                    x = mList[0]
                    y = self.destinationPath + '/IMG_' + "{:04}".format(count) + '.' + QFileInfo(x).suffix()
                    self.newText.emit('copying {} to {}'.format(x, y))
                    copyfile(x, y)
                    count = count + 1
                elif 0 == len(mList):
                    self.newText.emit('File {} could not be found, will be skipped.'.format(x))
                else:
                    self.newText.emit('Multiple files for {} have been found, file will be skipped.'.format(x))
        
        if(len(lines) != count-1):
            self.newText.emit('Warning: Could not copy all files!')
        self.newText.emit('Finished copying {} files of {}'.format((count-1), len(lines)))
        self.newText.emit('--------------------------------------------------------------------------------')

class MainWindow(QMainWindow):
    def __init__(self, src, dest):
        QMainWindow.__init__(self)
 
        self.setMinimumSize(QSize(640, 160))    
        self.setWindowTitle("Copy Images") 
        
        self.centralWidget = QWidget(self)          
        self.setCentralWidget(self.centralWidget)   
 
        self.layout = QVBoxLayout(self.centralWidget)
        
        self.source = QPushButton("Select src file (.txt list file of images)")
        self.layout.addWidget(self.source)
        self.source.released.connect(self.selectSource)
        
        self.destination = QPushButton("Select dest folder to copy the images to")
        self.layout.addWidget(self.destination)
        self.destination.released.connect(self.selectDestination)
        
        run = QPushButton("Start copy process")
        self.layout.addWidget(run)
        run.released.connect(self.copyFiles)
        
        self.textOutput = QTextEdit();
        self.layout.addWidget(self.textOutput)
        
        self.sourcePath = None
        self.destinationPath = None
        
        if None != src:
            self.selectSource(src)
            
        if None != dest:
            self.selectDestination(dest)
            
        self.copyThread = copyThread(src, dest)
        self.copyThread.newText.connect(self.writeText)
                
    def selectSource(self, src=None):
        if src == None:
            self.sourcePath, _ = QFileDialog.getOpenFileName(None, 'Choose the file to work with', '', 'Image list .txt (*.txt);; * (*.*)', '')
        else:
            self.sourcePath = src
        self.source.setText("Source: " + self.sourcePath)
        self.textOutput.append("Source selected: " + self.sourcePath)
    
    def selectDestination(self, dest=None):
        if dest == None:
            self.destinationPath = QFileDialog.getExistingDirectory(self, 'Choose the destination to copy to', '')
        else:
            self.destinationPath = dest
        self.destination.setText("Destination: " + self.destinationPath)
        self.textOutput.append("Destination: " + self.destinationPath)

    def copyFiles(self):
        if self.sourcePath is not None and self.destinationPath is not None:
            self.copyThread.sourcePath = self.sourcePath
            self.copyThread.destinationPath = self.destinationPath
            self.copyThread.start()
        else:
            self.textOutput.append('Please select a source file and a destination folder.')
          
    def writeText(self, line):
        self.textOutput.append(line)
        self.textOutput.ensureCursorVisible()
            
def main(argv):
    app = QtWidgets.QApplication(argv)
    parser = argparse.ArgumentParser(description='Copy images defined by a .txt file to a destination.')
    parser.add_argument('-src', type=str, help='path to a source file defining the images to copy')
    parser.add_argument('-dest', type=str, help='path to a folder to copy the images to')

    args = parser.parse_args()
        
    mainWin = MainWindow(args.src, args.dest)
    mainWin.show()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    main(sys.argv)
