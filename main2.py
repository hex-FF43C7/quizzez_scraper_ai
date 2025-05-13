import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


class OllamaClient:
    def __init__(self, ollama_url):
        self.ollama_url = ollama_url

    def send_question(self, question_and_answers: list, model="mistral:7b"):
        url = self.ollama_url
        headers = {"Content-Type": "application/json"}

        answers = '\n'.join([f"answer{k}: {v}" for k, v in question_and_answers[1].items()])
        complex_prompt = f"""what is the correct answer to the question: "{str(question_and_answers[0])}" with options: \n{answers}\nplease respond with just the title of the answer (ex: answer0, answer1, answer2, answer3, etc)"""

        # print(complex_prompt)

        data = {
            "model": model,
            "prompt": complex_prompt,
            "stream": False
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            # return response.json()['response']
            for i, (k, v) in enumerate(question_and_answers[1].items()):
                if re.search(rf"(answer{k})|({v})", response.text):
                    return int(k)
            return f"couldnt find opiton in {response.text}"
        else:
            return f"Error: {response.status_code} - {response.text}"


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

    GAMECODE = "148470"
    NAME = "Andrew W2"
    DRIVER_PATH = r'/Users/andrewwortmann/Documents/quizzez_scraper/chromedriver-mac-x64/chromedriver'
    OLLAMA_URL = "http://localhost:11434/api/generate"

    ollama_client = OllamaClient(OLLAMA_URL)
    scraper = QuizizzScraper(GAMECODE, NAME, DRIVER_PATH, ollama_client)

    # prompt = ["what are the first 3 letters of the alphabet?", {0: "abc", 1: "bfr", 2: "cjj"}]
    # response_text = ollama_client.send_question(prompt)
    # print(response_text)

    # prompt = ["what tool would you use to remove unwanted pixels from the side of an image", {0: "select", 1: "crop", 2: "paint"}]
    # response_text = ollama_client.send_question(prompt)
    # print(response_text)

    # prompt = ["wich is a video format", {0: ".flac", 1: ".mp4", 2: ".mp3", 3: ".png"}]
    # response_text = ollama_client.send_question(prompt)
    # print(response_text)

    try:
        scraper.login()
        for _ in range(5):
            q_screen = scraper.get_q_screen()
            print("Question and options:", q_screen)

            # Send the question and options to the Ollama container
            selected_option = ollama_client.send_question(q_screen)
            if "error" not in selected_option:
                print(f"Ollama selected option: {selected_option}")
                scraper.select_answer(selected_option)
            else:
                print("Failed to get a valid response from Ollama.")
                print("Ollama response:", selected_option)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.quit()
        print('dead')