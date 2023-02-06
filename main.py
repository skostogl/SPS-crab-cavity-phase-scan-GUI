from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import pyqtgraph as pg

import os
import numpy as np
import pandas as pd
import sys
from datetime import datetime

import run_ht_analysis

class MainWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        sys.exit()

    def __init__(self):
        super(MainWindow, self).__init__()

        # Load ui
        uic.loadUi('form.ui', self)

        # Set WindowTitle
        self.setWindowTitle("SPS CC phase scan application")
        
        # Set window size
        desktop = QDesktopWidget().availableGeometry()
        x = (desktop.width() - self.frameGeometry().width()) / 2
        y = (desktop.height() - self.frameGeometry().height()) / 2
        self.setGeometry(int(x), int(y), int(desktop.width()*0.7), int(desktop.height()*0.9))


        # Load all h5 files when file button is clicked
        self.pushButton_HT_load.clicked.connect(self.HT_path_loaded)
        self.pushButton_HT_load.setText("\U0001F4C1")
        
        # Possibility to increase rows in table with measurements (it is also done automatically)
        self.button_add_meas.clicked.connect(self.add_measurement)
        self.button_add_meas.setText("\U00002795 Add")

        # Possibility yo remove rows from measurements
        self.delete_button.clicked.connect(self.delete_row)
        self.delete_button.setText("\U00002796 Remove")
        

        # Initialize size of measurement table
        self.table_file_phase.setColumnWidth(0,270)
        self.table_file_phase.setColumnWidth(1,90)

        # Run button
        self.run_button.setStyleSheet("background-color : lightblue")
        self.run_button.clicked.connect(self.on_button_clicked)
        self.run_button.setText("\U00002192 Run")

        # Choose h5 files by clicking from file list
        self.HT_list_of_files.itemClicked.connect(self.item_clicked)

        ## CC name spin box
        self.CC_number.setPrefix("CC")
        self.CC_number.setSuffix(f",({cc1_name.upper()})")
        self.my_cc = cc1_name
        self.CC_number.valueChanged.connect(self.spin_updateLabel)
        
        # Load parquet twiss
        self.button_LoadTwiss.clicked.connect(self.load_twiss)
        
        # Plot
        self.graphWidget.setBackground('w')
        self.graphWidget.setLabel("bottom", "Phase (deg.)")
        self.graphWidget.setLabel("left", "CC Voltage (MV)")
        self.graphWidget.showGrid(x = True, y = True, alpha = 1)

        # Fit button
        self.fitButton.setEnabled(False)
        self.fitButton.clicked.connect(self.apply_fit)
        self.fitButton.setText("\U0001F4C8 Fit")

        # Default paths
        self.output_path.setPlainText(output_path)
        self.path_twiss.setPlainText(default_twiss_path)

        # Menu options
        self.actionScreenshot.triggered.connect(self.take_screenshot)
        #self.actionQuit.triggered.connect(self.closeEvent)

    # Possibility to take a screenshot of the mainwindow
    def take_screenshot(self):
        screenshot = self.grab()
        file_name, ok = QInputDialog.getText(self, "Save Screenshot", "Enter png file name:")
        if ok:
            file_name = str(file_name) + ".png"
            screenshot.save(file_name)

    # Tab analysis: Function to apply fit in final results
    def apply_fit(self):
        if len(self.final_results) == 0:
            self.message_fit = "No data to fit"
            self.fitresults.setPlainText(self.message_fit)
        else:
            try:
                fit_coeff = run_ht_analysis.run_fit(self.final_results, self.final_save_folder)

                angle=np.arange(-180, 190, 10)
                self.graphWidget.plot(angle, run_ht_analysis.test_func_B(np.array(angle), fit_coeff[0], fit_coeff[1], fit_coeff[2], fit_coeff[3]), pen=pg.mkPen('r', width=2, style=QtCore.Qt.DashLine))
            
                self.message_fit = "Fit results:\n"
                self.message_fit +=f'Voltage={fit_coeff[0]:.2f} MV \n'+r'Phase='+f'{fit_coeff[2]*180/np.pi:.2f} deg \n'+f'd={fit_coeff[3]:.2f} MV'
                self.fitresults.setPlainText(self.message_fit)
                self.message +=self.message_fit
            except Exception as e:
                self.create_message_popup(e)

    # Function that creates popup messages
    def create_message_popup(self, text, icon=QMessageBox.Critical):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"An error occurred: {text}")
            msg.setWindowTitle("Error")
            msg.exec_()
    
    # Tab optics: Load beta and phase advance values in CC & HT locations from twiss parquet
    def load_twiss(self):
        try:
            df_twiss = pd.read_parquet(self.path_twiss.toPlainText())
            self.my_beta_cc = df_twiss.at[self.my_cc, "bety"]
            self.my_beta_ht = df_twiss.at[ht_name, "bety"]
            self.my_muy_cc  = df_twiss.at[self.my_cc, "muy"]
            self.my_muy_ht  = df_twiss.at[ht_name, "muy"]
            self.my_dmuy    = self.my_muy_cc - self.my_muy_ht
            self.my_qy      = df_twiss.iloc[-1]["muy"]
            self.beta_HT.setText(str(round(self.my_beta_ht, 5)))
            self.beta_CC.setText(str(round(self.my_beta_cc, 5)))
            self.qy.setText(str(round(self.my_qy, 5)))
            self.dmu.setText(str(round(self.my_dmuy, 5)))
        except FileNotFoundError as e:
            print("File not found:", e)
            self.create_message_popup(e)
        except Exception as e:
            print("An unexpected error occurred:", e)
            self.create_message_popup(e)
    

    # Tab optics: CC name in spin box
    def spin_updateLabel(self):
        cc_names = [cc1_name, cc2_name]
        self.CC_number.setSuffix(f",({cc_names[self.CC_number.value() - 1].upper()})")
        self.my_cc = cc_names[self.CC_number.value() - 1]


    # Tab HT files: from list to measurement table
    def item_clicked(self, item):
        file_clicked = item.text()
        row_count = self.table_file_phase.rowCount()
        for row in range(row_count):
            if self.table_file_phase.item(row, 0):
                continue
            self.table_file_phase.setItem(row, 0, QTableWidgetItem(file_clicked))
            return
        self.add_measurement()
        self.table_file_phase.setItem(row_count, 0, QTableWidgetItem(file_clicked))
    # Tab HT files: possibility to add measurement rows in table
    def add_measurement(self):
        rowPosition = self.table_file_phase.rowCount()
        self.table_file_phase.insertRow(rowPosition) 

    # Tab HT files: possibility to delete measurement rows in table
    def delete_row(self):
        index = self.table_file_phase.currentRow()
        self.table_file_phase.removeRow(index)

    def HT_path_loaded(self):
        self.HT_list_of_files.clear()
        fname = QFileDialog.getExistingDirectory(self, "Select folder", default_ht_path)
        err_color = QColor('gray')
        self.textEdit_HT_path.setTextColor(err_color)
        self.textEdit_HT_path.setPlainText(fname)
        self.textEdit_HT_path.setReadOnly(True)
        self.HT_path = fname
        HT_files = [i for i in os.listdir(self.HT_path) if i.endswith(".h5")]
        self.ht_files = sorted(HT_files)[::-1] if HT_files else ["No h5 files found! Check the path"]
        self.HT_list_of_files.addItems(self.ht_files)
        if not self.ht_files:
            self.textEdit_HT_path.setTextColor(QColor('gray'))

    # Launch analysis
    def on_button_clicked(self):
        self.run_button.setStyleSheet("background-color: red;")
        self.run_button.setText("Running...")
        QApplication.processEvents()
        loop = QEventLoop()
        loop.processEvents()
        self.click_run()
        self.run_button.setStyleSheet("background-color: lightblue;")
        self.run_button.setText("Run")
        loop.exit()

    # Main function to run analysis
    def click_run(self):
        self.run_button.setStyleSheet("background-color : red")
        
        self.message_fit = ""
        self.fitresults.setPlainText(self.message_fit)
        self.message = ""
        self.analysis_text.setPlainText(self.message_fit)
    
        self.overwrite_files = self.overwrite.isChecked()
        self.final_ht_calibration_factor = float(self.ht_calibration.text())
        self.final_beta_CC = float(self.beta_CC.text())
        self.final_beta_HT = float(self.beta_HT.text())
        self.final_qy = float(self.qy.text())
        self.final_dmu = float(self.dmu.text())
        self.final_energy_gev = float(self.energy_gev.text())
        self.final_save_folder = self.output_path.toPlainText()
        self.final_HT_path = self.textEdit_HT_path.toPlainText()

        try:
            filenames = []
            phases    = []
            for nb_row in range(self.table_file_phase.rowCount()):
                if self.table_file_phase.item(nb_row,0) and self.table_file_phase.item(nb_row,1):
                    filenames.append(self.table_file_phase.item(nb_row,0).text())
                    phases.append(self.table_file_phase.item(nb_row,1).text())
            self.final_filename_dict = pd.DataFrame({"filename": filenames, "deg": phases})
            self.final_filename_dict = self.final_filename_dict[(self.final_filename_dict.filename!='') & (self.final_filename_dict.deg!='')]
            if len(self.final_filename_dict)==0:
                e = "No h5 files specified!"
                print("An error occurred:", e)
                self.create_message_popup(e)

            self.final_filename_dict.deg=self.final_filename_dict.deg.astype(float)
            self.final_filename_dict.sort_values(by='deg', inplace=True)
            self.final_filename_dict.reset_index(inplace=True)

            now = datetime.now()
            self.message = f"Application launched at {now}\n\n"
            self.message += f"Running with the following parameters:\n"
            self.message+= f"HT calibration factor: {self.final_ht_calibration_factor}\nBety (m) in CC {self.my_cc}: {self.final_beta_CC}\nBety (m) in HT {ht_name}: {self.final_beta_HT}\nQy: {self.final_qy}\nDmuy CC-HT: {self.final_dmu}\nEnergy (GeV): {self.final_energy_gev} \n"
            self.message+=f"\nFilenames considered:\n {self.final_filename_dict}"

            self.analysis_text.setPlainText(self.message)
       
            self.final_filename_dict_copy = self.final_filename_dict.copy()

            if self.overwrite_files==False:
                temp_files = []
                temp_phase = []
                self.message += "\n\nResult files will not be overwritten\n"
                for counter, file in enumerate(self.final_filename_dict["filename"]):
                    myfile = f"{self.final_save_folder}/results_{file}.parquet"
                    if not os.path.exists(myfile):
                        temp_files.append(file)
                        temp_phase.append(self.final_filename_dict["deg"][counter])
                    else:
                        self.message += f"Results from {file} already exist in output path, will not repeat the analysis.\n"
                self.final_filename_dict = {"filename": temp_files, "deg": temp_phase}
                self.analysis_text.setPlainText(self.message)
                
            results, analysis_message = run_ht_analysis.ht_analysis(self.final_HT_path, self.final_energy_gev, self.final_filename_dict, self.final_beta_HT, self.final_qy, self.final_beta_CC, self.final_dmu, self.final_ht_calibration_factor, self.final_save_folder)
            
            appended_data = []
            for file in self.final_filename_dict_copy["filename"]:
                appended_data.append(pd.read_parquet(f"{self.final_save_folder}/results_{file}.parquet"))
            results = pd.concat(appended_data)
            results.rename(columns={'voltage': 'myVcc at t zero[MV]', 'phase': 'deg'}, inplace=True)
            results.to_parquet(f"{self.final_save_folder}/results.parquet")
            results["deg"] = results.deg.astype(float)
            results.sort_values(by="deg", inplace=True)
            results.reset_index(inplace=True)

            self.graphWidget.clear()
            self.graphWidget.plot(results.deg, results["myVcc at t zero[MV]"], symbol='s', symbolSize = 10)

            now = datetime.now()
            self.message+=analysis_message
            self.message += f"\n\nApplication finished at {now}\n\n"
            self.analysis_text.setPlainText(self.message)

            self.final_results = results
            
            self.fitButton.setEnabled(True)

        except Exception as e:
            print("An error occurred:", e)
            self.create_message_popup(e)


def main():
    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    # Some default names and paths
    current_date = datetime.now().strftime("%d%m%Y")
    current_path = os.getcwd()

    default_ht_path    = f"{current_path}/copied_data_HT/2022_09_28"
    default_twiss_path = f"{current_path}/sps_madx/twiss_SPS_q20.parquet"
    output_path        = f"{current_path}/results_{current_date}"

    cc1_name = "acfca.61739"
    cc2_name = "acfca.61740"
    ht_name  = "bpcl.42171"
    main()
        


# %%
