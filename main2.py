import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class OllamaClient:
    def __init__(self, ollama_url):
        self.ollama_url = ollama_url

    def send_question(self, question_and_answers):
        try:
            # Prepare the payload
            payload = {
                "question": question_and_answers[0],
                "options": question_and_answers[1]
            }
            # Send the request to the Ollama container
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()  # Return the parsed JSON response
        except Exception as e:
            print(f"Error communicating with Ollama container: {e}")
            return None


class QuizizzScraper:
    def __init__(self, game_code, name, driver_path, ollama_client):
        self.game_code = game_code
        self.name = name
        self.driver = webdriver.Chrome(service=webdriver.ChromeService(executable_path=driver_path))
        self.ollama_client = ollama_client

    def login(self):
        self.driver.get("https://quizizz.com/join")

        # Enter game code
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-cy='gamecode-field']"))
        )
        game_code_field = self.driver.find_element(By.CSS_SELECTOR, "input[data-cy='gamecode-field']")
        game_code_field.send_keys(self.game_code)
        game_code_field.submit()

        # Enter name
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-cy='enter-name-field']"))
        )
        name_field = self.driver.find_element(By.CSS_SELECTOR, "input[data-cy='enter-name-field']")
        name_field.send_keys(self.name)
        name_field.submit()

    def get_q_screen(self):
        # Wait for the question text to appear
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='text-container'] p[style='display:inline']"))
        )
        time.sleep(1)  # Covers a little bit of the loading time
        question = self.driver.find_element(By.CSS_SELECTOR, "div[data-cy='text-container'] p[style='display:inline']")
        question_and_answer = [question.text, {}]

        # Retrieve options
        answer = 0
        while self._option_exists(answer):
            option_button = self.driver.find_element(By.CSS_SELECTOR, f"button[data-cy='option-{answer}']")
            option_text = option_button.find_element(By.CSS_SELECTOR, "p[style='display:inline']").text
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
    NAME = "Andrew W100"
    DRIVER_PATH = r'/Users/andrewwortmann/Documents/quizzez_scraper/chromedriver-mac-x64/chromedriver'
    OLLAMA_URL = "http://localhost:11434/answer"

    ollama_client = OllamaClient(OLLAMA_URL)
    scraper = QuizizzScraper(GAMECODE, NAME, DRIVER_PATH, ollama_client)

    try:
        scraper.login()
        for _ in range(5):
            q_screen = scraper.get_q_screen()
            print("Question and options:", q_screen)

            # Send the question and options to the Ollama container
            response = ollama_client.send_question(q_screen)
            if response and "selected_option" in response:
                selected_option = response["selected_option"]
                print(f"Ollama selected option: {selected_option}")
                scraper.select_answer(selected_option)
            else:
                print("Failed to get a valid response from Ollama.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.quit()
        print('dead')