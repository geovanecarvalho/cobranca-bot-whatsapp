import sys
import csv
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
from datetime import datetime 
from time import sleep
import os


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("cobranca.ui",self)
        self.btnProcurar.clicked.connect(self.browsefiles)
        self.btnEnviar.clicked.connect(self.enviarMensagem)
        self.lista_cliente = []
        self.contatos_nao_enviados = []
        self.contEnvio = 0
        self.contNaoEnvio = 0
    

    def browsefiles(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file', 'C:/Users/Geovane/Desktop/', 'CSV (*.csv)')
        self.txtFile.setText(fname[0])


    def enviarMensagem(self):
        if self.txtFile.text() != "":
            servico = Service(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=servico)
            path = self.txtFile.text()
            mensagem = ""

            
            with open(path, "r") as file:
                file_csv = csv.reader(file ,delimiter=";")
                for linha in file_csv:
                    self.lista_cliente.append(linha)

            for nome, telefone in self.lista_cliente:
                data = datetime.now()
                data_atual = data.strftime('%d/%m/%Y')
                horas = str(datetime.now())
                horas = int(horas[11:-13])

                if horas >= 6 and horas < 12:
                        mensagem = f"Bom dia! *{nome}*, aqui é do Cemitério Jardim Paraiso. Em nosso sistema, foram encontrados débitos anteriores à *{data_atual}*. Por favor entre em contato conosco para regularização. Caso já tenha sido pago, por favor desconsiderar."
        
                elif horas >=12 and horas < 18:
                        mensagem = f"Boa tarde! *{nome}*, aqui é do Cemitério Jardim Paraiso. Em nosso sistema, foram encontrados débitos anteriores à *{data_atual}*. Por favor entre em contato conosco para regularização. Caso já tenha sido pago, por favor desconsiderar." 
        

                mensagem = quote(mensagem)

                    
                
                url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem}"
                browser.get(url)

                while len(browser.find_elements(By.ID, 'side')) < 1:
                    sleep(1)
                sleep(5)
                if len(browser.find_elements(By.XPATH, '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[1]')) < 1:
                    self.contEnvio += 1
                    browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div/span').click()
                    sleep(2)
                    browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/div/ul/li[1]/button/input').send_keys(os.path.abspath("./jardimParaiso.png"))
                    sleep(2)

                    browser.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div').click()
                    
                    sleep(2)
                else:
                    self.contNaoEnvio += 1
                    self.contatos_nao_enviados.append([nome, telefone])
                
            with open('./log/contatos_nao_enviados.csv', "a") as file:
                for contato in self.contatos_nao_enviados:
                    csv.writer(file, delimiter=';').writerow(contato)
                
            msg = QMessageBox()
            msg.setWindowTitle("Enviadas com Sucesso!")
            msg.setText(f"Enviadas: {self.contEnvio}\nNão enviadas: {self.contNaoEnvio}")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Upload de Arquivo")
            msg.setText("Upload de arquivo csv é obrigatório")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()      
                
                       
    
    

app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(400)
widget.setFixedHeight(404)
widget.show()
sys.exit(app.exec_())