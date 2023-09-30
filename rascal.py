#!/usr/bin/env python3.11

__version__ = "1.0"
__author__ = "Jesse Shelley"
__email__ = "max@anti-forensics.com"

import argparse
import os
import sys
import Core.post_form_login
import Core.settings
import Core.basic_auth_login
from termcolor import colored


def main() -> None:
    parser = argparse.ArgumentParser(description="Concurrent login brute forcer.")
    parser.add_argument('--post', required=False,
                        default=None, action="store_true",
                        help="Specify a form login using POST.")
    parser.add_argument('--basic', required=False,
                        default=None, action="store_true",
                        help="Attempt basic authentication.")
    parser.add_argument('-u', '--url', required=True, type=str,
                        default=None, dest="url",
                        help="Specify URL to fuzz (e.g. www.google.com/search?q=FUZZ")
    parser.add_argument('-w', '--wordlist', required=True, type=str,
                        default=None, dest="wordlist",
                        help='Specify wordlist to use (e.g. /usr/share/wordlists/dirb/commmon.txt)')
    parser.add_argument('--username', required=True, type=str,
                        default=None, dest="username",
                        help="Specify a username to attack.")
    parser.add_argument('--username_field', required=False, type=str,
                        default=None, dest="username_field",
                        help="Specify the form field name for the username input.")
    parser.add_argument('--password_field', required=False, type=str,
                        default=None, dest="password_field",
                        help="Specify the form field name for the password input.")
    parser.add_argument('--success_text', required=False, type=str,
                        default=None, dest="success_text",
                        help="Specify a login successful message to compare against.")
    parser.add_argument('--failure_text', required=False, type=str,
                        default=None, dest="failure_text",
                        help="Specify a login failure message to compare against.")
    parser.add_argument("--get_proxies", dest="proxies", required=False,
                        action='store_true',
                        help='Gather socks4/socks5 elite proxies.')
    parser.add_argument("-sc", dest="session_cookie", required=False,
                        help='Specify a session cookie.')
    parser.add_argument("--cua", dest="custom_user_agent", required=False,
                        help='Set a custom user agent.')
    parser.add_argument("-v", "--version", required=False,
                        action="store_true",
                        help="Display software version.")

    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        print(f"Specify a url: -u/--url")
        sys.exit(1)

    if args.wordlist:
        wordlist = args.wordlist
    else:
        print(f"Specify a password wordlist: -w/--wordlist")
        sys.exit(1)

    if args.username:
        username = args.username
    else:
        print(f"Specify a username: --username")
        sys.exit(1)

    if not args.basic and args.post:
        if args.username_field:
            username_field = args.username_field
        else:
            print(f"Specify a form field name for the username: --username_field <userid>")
            sys.exit(1)

        if args.password_field:
            password_field = args.password_field
        else:
            print(f"Specify a form field name for the password: --password_field <passwd>")
            sys.exit(1)

    if args.custom_user_agent:
        Core.settings.custom_user_agent = args.custom_user_agent

    if args.success_text and args.failure_text:
        print(f"Please provide either a --success_text or --failure_text message to compare against, not both.")
        sys.exit(0)

    success_text = args.success_text
    failure_text = args.failure_text

    if not success_text and not failure_text:
        print(f'Supply a "--success_text" or a "--failure_text" parameter. This value indicates text on the login'
              f' page after either a successful or failed login attempt.')
        sys.exit(1)

    if args.post:
        print(f"""
        -- SETTINGS VERIFICATION --
        {colored(f"scheme: {url.split(':')[0]}", "yellow", attrs=['blink'])}
        url: {url}
        username: {username}
        password list: {wordlist}
        username post form field: {username_field}
        password post form field: {password_field}
        success message: {success_text}
        failure message: {failure_text}
        custom user agent: {Core.settings.custom_user_agent}
        """)

        answer = input("Does this look OK? (Y/n) ")
        if answer == "":
            answer = "Y"
        if answer.lower() != "y":
            sys.exit(0)

        pfl = Core.post_form_login.PostFormLogin(url, wordlist, username, username_field, password_field,
                                                 success_text, failure_text)
        pfl.build_password_list()  # initialize password wordlist in memory
        pfl.login_workers()

    if args.basic:
        print(f"""
        -- SETTINGS VERIFICATION --
        {colored(f"scheme: {url.split(':')[0]}", "yellow", attrs=['blink'])}
        url: {url}
        username: {username}
        password list: {wordlist}
        success message: {success_text}
        failure message: {failure_text}
        custom user agent: {Core.settings.custom_user_agent}
        """)

        answer = input("Does this look OK? (Y/n) ")
        if answer == "":
            answer = "Y"
        if answer.lower() != "y":
            sys.exit(0)

        bal = Core.basic_auth_login.BasicAuthLogin(url, username, wordlist,
                                                   success_text, failure_text)
        bal.build_password_list()  # initialize password wordlist in memory
        bal.login_workers()

    if not args.basic and not args.post:
        print(f"Specify an operation/method type (E.g. --basic/--post).")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"Killing application...")
        pid = os.getpid()
        os.kill(pid, 9)
    except Exception as e:
        print(e)
