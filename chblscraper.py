import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from bs4 import BeautifulSoup
import requests


class CHBLScraper(QWidget):
    def __init__(self):
        super(CHBLScraper, self).__init__()
        self.directory = ""
        self.initUI()

    def initUI(self):
        self.qgl = QGridLayout()

        self.url = QLineEdit()
        self.url.setPlaceholderText("Chrysanthemum URL")
        self.url.setFixedSize(200, 20)
        self.qgl.addWidget(self.url)

        self.btn_pick = QPushButton("Save file to...")
        self.btn_pick.clicked.connect(self.pick_directory)
        self.qgl.addWidget(self.btn_pick)

        self.btn_download = QPushButton("Download")
        self.btn_download.clicked.connect(self.download)
        self.qgl.addWidget(self.btn_download)

        self.setLayout(self.qgl)
        self.setWindowTitle("Chrysanthemum Downloader")
        self.setFixedSize(320, 100)
        self.show()

    def show_result(self, novel_title, chapter_title):
        msg = QMessageBox()
        msg.setWindowTitle("File has been downloaded")
        msg.setText(novel_title)
        msg.setIcon(QMessageBox.Information)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setInformativeText(
            f"{chapter_title} has been downloaded to {self.directory}."
        )

        msg.exec_()

    @pyqtSlot()
    def pick_directory(self):
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

    def show_error(self):
        msg = QMessageBox()
        msg.setWindowTitle("Error!")
        msg.setText("Cannot save file")
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText("Please pick a folder/directory.")
        msg.setDefaultButton(QMessageBox.Ok)

        msg.exec_()

    @pyqtSlot()
    def download(self):
        if not self.directory:
            self.show_error()
            return

        self.btn_download.setEnabled(False)
        bl_story = requests.get(self.url.text())
        soup = BeautifulSoup(bl_story.content, features="html.parser")

        header = soup.find_all("header", {"class": "entry-header"})
        post_title = header[0].find_all("span", {"class": "chrys-post-title"})
        novel_title = chapter = ""
        for title in post_title:
            novel_title = title.find("a", attrs={"class": "novel-title"}).text
            chapter = title.find("span", attrs={"class": "chapter-title"}).text
            chbl_file = f"{self.directory}/{novel_title} - {chapter}.txt"
            with open(chbl_file, "a+") as t:
                separator = "".join(["=" * 20])
                t.writelines(
                    f"{separator}\n{novel_title}\n{chapter}\n{separator}\n\n"
                )

        # Assumption: novel-content is always unique in a page
        content = soup.find_all("div", attrs={"id": "novel-content"})
        style = "height:1px;width:0;overflow:hidden;display:inline-block"
        for paragraph in content[0].find_all("p"):
            to_append = paragraph.text
            if "Author" in paragraph.text and "Corner" in paragraph.text:
                break
            if (
                paragraph.get("style") and paragraph["style"] == style
            ) or paragraph.find_all("span", attrs={"class": "jum"}):
                continue
            with open(chbl_file, "a+") as t:
                if paragraph.find_all("span", {"style": style}):
                    to_append = to_append[:-6]
                t.writelines(to_append + "\n\n")
        self.show_result(novel_title, chapter)
        self.btn_download.setEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.download()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = CHBLScraper()
    sys.exit(app.exec_())
