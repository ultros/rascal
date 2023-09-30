import base64
import os
import Core.settings
import requests
import concurrent.futures

i = 0  # Global for keeping track of current password and total passwords.
password_count = 0  # Total passwords from password list
hard_quit = False  # Stop worker threads; global state


class BasicAuthLogin(Core.settings.Settings):
    def __init__(self, url: str, username: str, wordlist: str, success_text: str, failure_text: str) -> None:
        Core.settings.Settings.__init__(self)
        self.url = url
        self.username = username
        self.wordlist = wordlist
        self.passwords = []
        self.success_text = success_text
        self.failure_text = failure_text

    def build_password_list(self) -> None:
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

    def perform_login(self, password: str) -> None:
        """
        Attempts to log in using credential data and POST method
        """
        global hard_quit
        global i
        global password_count

        if hard_quit:  # stops worker threads (killing process) on ctrl+c or username/password found
            pid = os.getpid()
            os.kill(pid, 9)

        headers = {}

        try:
            auth_string = self.username + ":" + password
            auth_string = base64.b64encode(auth_string.encode("UTF-8"))
            headers = {
                'Authorization': f'Basic {auth_string.decode()}'
            }
        except Exception as e:
            print(e)

        response = requests.get(self.url, headers=headers)

        if response.cookies:
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
            if i == 0:
                if response.headers:
                    print(f"""
    ##########
    Sample of response headers.
    I.e., Build your failure string from header details:
    {response.headers['WWW-Authenticate']}
    ##########
    """)

            if self.failure_text in response.text or self.failure_text in str(response.headers):
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