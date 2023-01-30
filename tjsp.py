from base import Base
from selenium.webdriver.common.by import By
import json


class TJSP(Base):
    def __init__(self, max_results, search):
        super().__init__()
        self.max_results = max_results
        self.search = search
        self.dados = []
        self.n_resultados = 0

    def access_tjsp(self):
        driver = self.get_driver()
        driver.get("https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do")

    def _search(self):
        driver = self.get_driver()
        driver.find_element(
            By.ID, "iddados.buscaInteiroTeor").send_keys(self.search)
        driver.find_element(By.ID, "pbSubmit").click()

    def get_data_page(self):
        # get all .fundocinza1 elements
        driver = self.get_driver()
        self.wait(2)
        # self.espande_ementas()
        caixas_dados = driver.find_elements(By.CLASS_NAME, "fundocinza1")
        data = []
        for caixa in caixas_dados:
            try:
                if len(self.dados) < self.max_results:
                    dado = {}
                    # get a .esajLinkLogin text
                    id = caixa.find_element(By.CLASS_NAME, "esajLinkLogin").text
                    # get .ementaClass2 elements
                    infos = caixa.find_elements(By.CLASS_NAME, "ementaClass2")
                    classe_assunto = infos[0].find_element(
                        By.CSS_SELECTOR, "td").text
                    # split by "/" and get the last element
                    classe_assunto = classe_assunto.split("/")[-1].strip().lower()

                    has_ementa = (
                        infos[-1].find_element(By.CSS_SELECTOR, "strong").text == "Ementa:")
                    if classe_assunto != self.search or not has_ementa:
                        continue
                    dado['id'] = id
                    dado['assunto'] = classe_assunto
                    for info in infos[:-1]:
                        key = info.find_element(By.CSS_SELECTOR, "strong").text
                        value = info.find_element(By.CSS_SELECTOR, "td").text
                        # remove the element strong
                        value = value.replace(key, "")
                        # remove ":" from key
                        key = key.replace(":", "")
                        # remove spaces around the key and value
                        key = key.strip()
                        value = value.strip()
                        dado[key] = value
                    # get the last of the two divs inside the last .ementaClass2
                    ementa_element = infos[-1].find_elements(
                        By.CSS_SELECTOR, "div")[-1]
                    self.get_driver().execute_script(
                        "arguments[0].setAttribute('style', 'display: block;')", ementa_element)
                    key = ementa_element.find_element(
                        By.CSS_SELECTOR, "strong").text
                    value = ementa_element.text
                    value = value.replace(key, "")
                    key = key.replace(":", "")
                    key = key.strip()
                    value = value.strip()
                    dado[key] = value
                    self.dados.append(dado)
                    print(len(self.dados), "de", self.max_results)
            except Exception as e:
                print("erro inesperado", e)
                continue

    def get_n_results(self):
        # #nomeAba-A
        driver = self.get_driver()
        n_results = driver.find_element(By.ID, "nomeAba-A").text
        # remove all non numeric characters
        n_results = "".join([char for char in n_results if char.isnumeric()])
        self.n_resultados = int(n_results)

    def colhe_dados(self):
        self.access_tjsp()
        self._search()
        self.get_n_results()
        print("Coletando dados...")
        print(self.n_resultados, "resultados encontrados")
        self.varre_paginas()

    def next_page(self):
        self.wait()
        driver = self.get_driver()
        # select one div .trocaDePagina
        troca_pagina = driver.find_elements(By.CLASS_NAME, "trocaDePagina")[0]
        # get the last element inside the div, a or span
        last_element = troca_pagina.find_elements(By.XPATH, "./*")
        # if the last element is a, click on it then return True
        if last_element[-1].tag_name == "a":
            last_element[-1].click()
            return True
        return False

    def varre_paginas(self):
        next_page = True
        while len(self.dados) < self.max_results:
            if next_page:
                self.get_data_page()
                next_page = self.next_page()

    def gera_json(self, file_name= "dados"):
        if file_name == "dados":
            file_name = self.search
        # createa a json file with the data
        self.colhe_dados()
        with open("./datasets/"+file_name + ".json", "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)
