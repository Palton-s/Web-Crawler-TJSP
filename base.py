from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import user
from time import sleep

class Base:

    max_wait_element = 5
    debug = True
    headless = user.headless
    errros = []
    messages = []
    width = 1920
    height = 1080
    initial_time = time.time()

    def xprint(self, *args, **kwargs):
        print(*args, **kwargs)

    def execution_time(self):
        return round(time.time() - self.init_time,0)

    def print(self,args):
        if self.debug:
            pass_time = round(self.get_execution_time(), 1)
            self.xprint(args+" - "+str(pass_time))

    def __init__(self):
        self.init_execution_time = time.time()
        
    def get_execution_time(self):
        return round(time.time() - self.init_execution_time,0)


    def set_options(self, options):
        self.options = options
    
    def get_options(self):
        if hasattr(self, 'options'):
            return self.options
        else:
            self.options = Options()
            self.options.headless = self.headless
            self.options.profile = webdriver.FirefoxProfile()  

            return self.options

    def get_driver(self):
        if not hasattr(self, 'driver'):    
            options=self.get_options()
            self.driver = webdriver.Firefox(options=options)
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(self.width, self.height)
        return self.driver
    
    def wait_element(self, By_, selector, time=max_wait_element):
        driver = self.get_driver()
        try:
            Element = WebDriverWait(driver, time).until(
                EC.presence_of_element_located((By_, selector))
            )
        except:
            self.print("Elemento não encontrado")
            return None

        return Element


    def tearDown(self):
        self.print("Fechando navegador")
        driver = self.get_driver()
        driver.close()
    
    def request(self, url):
        driver = self.get_driver()
        driver.get(url)
        return driver

    def wait(self, time=1):
        sleep(time)
