from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class QuizizzScraper:
    def __init__(self, game_code, name, driver_path):
        self.game_code = game_code
        self.name = name
        self.driver = webdriver.Chrome(service=webdriver.ChromeService(executable_path=driver_path))

    def login(self):
        self.driver.get("https://quizizz.com/join")

        # Enter game code
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-cy='gamecode-field']"))
        )
        # time.sleep(2)
        game_code_field = self.driver.find_element(By.CSS_SELECTOR, "input[data-cy='gamecode-field']")
        game_code_field.send_keys(self.game_code)
        # time.sleep(2)
        game_code_field.submit()

        # Enter name
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-cy='enter-name-field']"))
        )
        # time.sleep(2)
        name_field = self.driver.find_element(By.CSS_SELECTOR, "input[data-cy='enter-name-field']")
        name_field.send_keys(self.name)
        # time.sleep(2)
        name_field.submit()

    def get_q_screen(self):
        # Wait for the question text to appear
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='text-container'] p[style='display:inline']"))
        )
        time.sleep(1) #covers a little bit of the loading time
        question = self.driver.find_element(By.CSS_SELECTOR, "div[data-cy='text-container'] p[style='display:inline']")
        # print(question.text)
        question_and_answer = [question.text, {}]

        # Retrieve options
        answer = 0
        while self._option_exists(answer):
            option_button = self.driver.find_element(By.CSS_SELECTOR, f"button[data-cy='option-{answer}']")
            option_text = option_button.find_element(By.CSS_SELECTOR, "p[style='display:inline']").text
            # print(option_text)
            question_and_answer[1][answer] = option_text
            answer += 1
        
        return question_and_answer
    
    def select_answer(self, answer):
        # Select the answer
        try:
            option_button = self.driver.find_element(By.CSS_SELECTOR, f"button[data-cy='option-{answer}']")
            option_button.click()
        except Exception as e:
            print(f"Error selecting answer {answer}: {e}")

    def _option_exists(self, index):
        try:
            self.driver.find_element(By.CSS_SELECTOR, f"button[data-cy='option-{index}']")
            return True
        except:
            return False

    def quit(self):
        self.driver.quit()


if __name__ == "__main__":
    GAMECODE = "092883"
    NAME = "Andrew W10"
    DRIVER_PATH = r'/Users/andrewwortmann/Documents/quizzez_scraper/chromedriver-mac-x64/chromedriver'

    scraper = QuizizzScraper(GAMECODE, NAME, DRIVER_PATH)
    try:
        scraper.login()
        for _ in range(5):
            print(scraper.get_q_screen())
            scraper.select_answer(int(input("Enter the answer number: ")))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.quit()
        print('dead')