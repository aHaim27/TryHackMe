## 🐲 Team - TryHackMe Write-up

## 📌 Overview
A beginner friendly boot2root machine, 

Target IP: 10.112.162.190

> Note: I suggest people who try this room to go over the following rooms before:
> - nmap
> - gobuster
> - ffuf
> - file inclusion

---

## 1. Reconnaissance: 🔍
Used Nmap to scan the target IP with the following command:
```bash
nmap -sV -sC -p- -T5 --min-rate 1000 -A -O 10.112.162.190
```

Found the following services running:
21/tcp open  ftp     vsftpd 3.0.5
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))


---

## 2. Reaching to the HTTP service using a browser: 🦊
Using the Firefox browser I went to the HTTP and it showed the default Apache service page.
I checked the source code for any leads and found the following note:
```http
<title>Apache2 Ubuntu Default Page: It works! If you see this add 'team.thm' to your hosts!</title>
```
<img width="1253" height="1140" alt="Screen Shot 2026-06-27 at 09 42 01 AM" src="https://github.com/user-attachments/assets/7815a2cf-ac9c-44ef-8cb5-80a30078a033" />

Following the note at header, I added the hostname "team.thm" to the IP using:
```bash
nano /etc/hosts
```

And continued to investigate the web application by looking for the newly added URL:
```URL
http://team.thm
```

The following page was loaded:
<img width="2056" height="1059" alt="Screen Shot 2026-06-27 at 12 50 03 PM" src="https://github.com/user-attachments/assets/1a454eb8-8710-4983-a308-d2f53c9fedc3" />

No further information was discoverd while searching the source code. I moved on to enumarting with gobuster.

---

## 3. Enumartion with Gobuster: 🔎
I used the following command to check for any directories, ".txt" files and ".php" files:


```bash
gobuster dir -u 'http://team.thm' -w /usr/share/wordlists/dirb/big.txt -x .txt,.php -t 64
```


And got the following results:
<img width="1314" height="767" alt="Screen Shot 2026-06-27 at 13 01 41 PM" src="https://github.com/user-attachments/assets/35797d39-d74c-4938-952e-5c2da706db7d" />


When checking the contents of "robots.txt" I found it had the following string in it:

> "dave"

I figured it might be some user of the system. I didn't have access to /scripts and /assets so I used gobuster to enumarte in them too:


/scripts:
<img width="1693" height="991" alt="Screen Shot 2026-06-27 at 13 04 06 PM" src="https://github.com/user-attachments/assets/ac6f4038-aa1b-4b67-89da-fab026926c42" />
---

/assets:
<img width="1398" height="701" alt="Screen Shot 2026-06-27 at 13 05 07 PM" src="https://github.com/user-attachments/assets/72484335-f4f0-4ca8-8412-1a0e4b302efd" />
---

I wanted to check out scripts.txt and it was an intersting find:
<img width="1121" height="530" alt="Screen Shot 2026-06-27 at 13 07 14 PM" src="https://github.com/user-attachments/assets/79b2ed7c-4803-4b33-a0de-b666e25242b0" />

Reading this file shows that we have a file named "script" that had a different extension, and in this file we have the creds unredacted!

---

## 4. Using FFUF to find the extension of the old "script" file: 👴🏼
I used FFUF with the next command to search for a file named "script" on 'http://team.thm/scripts' and got the following hit!
```bash
ffuf -u 'http://team.thm/scripts/script.FUZZ' -w /usr/share/wordlists/Seclists/Discovery/Web-Content/big.txt
```
<img width="1548" height="625" alt="Screen Shot 2026-06-27 at 13 13 54 PM" src="https://github.com/user-attachments/assets/eb841abe-e4f1-46df-846d-325c71ada6ad" />

Pretty easy to understand which extension is related to the old version here. I checked the contents and got the following creds:
<img width="1524" height="910" alt="ffuf_scan" src="https://github.com/user-attachments/assets/27839e8e-c95b-4289-b91b-c40d6c8331c2" />


---

## 5. Connecting to the FTP service in the machine using the above creds: 🛡️
To connect to the ftp service I simply used the following format:
```bash
ftp 10.112.162.190
```
and entered the Username and Password. the service had passive mode enabled so using "passive" command I disabled it and got to work:
<img width="1361" height="483" alt="Screen Shot 2026-06-27 at 13 26 10 PM" src="https://github.com/user-attachments/assets/93a86ba6-4da9-4e98-a647-ab225e3b7a21" />

I figured that the message talks about a subdomain within team.thm so I added it as hostname at /etc/hosts and checked the website.

---

## 6. Viewing the website: 👀
When logging into the web page at the subdomain we can see the a link that transfers us to:
> http://dev.team.thm/script.php?page=teamshare.php

I saw the "?page=" with a file after it and checked for LFI by replacing "teamshare.php" with "/etc/passwd". Vulnerability was found succesfully.

I wanted to find the names of the users in the system so I used the command:
```bash
curl 'http://dev.team.thm/script.php?page=/etc/passwd' | grep /bin/bash
```

and got a hit on:
- root
- dale
- gyles

---

## 7. Fuzzing ?page= for intersting files: 📁
I used FFUF to and seclists to find intersting files I have access to that are bigger in size than "1" using the following command:
```bash
ffuf -u 'http://dev.team.thm/script.php?page=FUZZ' -w wordlists/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt -t 64 -fs 1
```
results are in [outputs/ffuf.results](outputs/ffuf.results).

An intersting find was at /etc/ssh/sshd_config. remember Gyles said to Dale: "make a copy of your "id_rsa" and place this in the relevent config file."? well, he did.
it was there:

<img width="439" height="514" alt="Screen Shot 2026-06-27 at 19 34 43 PM" src="https://github.com/user-attachments/assets/44f2b2a6-495d-400a-acbc-915202d19192" />

since it was used as a comment with "#" I used Cyberchef to replace the "#" with nothing:

<img width="1403" height="997" alt="Screen Shot 2026-06-27 at 19 37 43 PM" src="https://github.com/user-attachments/assets/11befe9e-1e80-47b1-817c-4abacd017c9d" />

I saved the key using:
```bash
leafpad id_rsa
```

Well. now that I have the key and username, I want to try a ssh connection.

---

## 8. Connecting using SSH: 🔐
(Paused for lunch here and the machine turned off. I restarted it and it changed it's IP to 10.112.174.79)
I had an error saying the key is not protected because it's permissions should only allow me to use it. so I changed the permissions to 600 using:

```bash
chmod 600 id_rsa
```

and now it worked!
<img width="803" height="326" alt="Screen Shot 2026-06-27 at 19 48 24 PM" src="https://github.com/user-attachments/assets/efd682b6-2143-4f31-88b9-07d6bf013d61" />

---

## 9. Privilege Escaltion: 🧗🏼‍♂️
I checked what commands I can sudo and found: "/home/gyles/admin_checks"
I checked the code and analyzed it for vulnerabities. I found it takes any error from the date stamp and executes it. I wanted to manipulate it to get a shell as gyles.
<img width="1178" height="836" alt="Screen Shot 2026-06-27 at 20 00 33 PM" src="https://github.com/user-attachments/assets/1c94dfb7-b377-4277-b0d2-b5feff9b71ed" />

In the attempt above, I used the "admin_checks" as gyles, used the vulnerability in the error handling method, used it to make a shell command and created a shell using:
```python
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

## 10. You guessed it, MORE ESCALATION!! 🔝
I tried getting to root but didn't have the permissions needed. I tried to check for sudo commands but needed a password so I skipped. I checked for running processes with "ps aux" but the processes were cut out:

<img width="919" height="1084" alt="Screen Shot 2026-06-27 at 20 06 08 PM" src="https://github.com/user-attachments/assets/e21ba4ae-bad7-4f44-b982-bddd5027c5c5" />

I used "ps auxww" after checking how to expand it and didn't find something useful.

I checked "journalctl" to see if there was any recent activity by root that I may be able to manipulate. nothing found yet.

I tried checking with crontab for any root activity and didn't find any for mine or root.
<img width="799" height="513" alt="Screen Shot 2026-06-27 at 20 19 18 PM" src="https://github.com/user-attachments/assets/98edf13e-9aec-49da-b1b7-19099b02e2b5" />

I then tried checking specificly for scheduled tasks in the /var/log/syslog using:

```bash
grep -i cron /var/log/syslog
```

Nothing.
<img width="562" height="39" alt="Screen Shot 2026-06-27 at 20 21 33 PM" src="https://github.com/user-attachments/assets/5c49b3a0-b5c8-4e5a-90e6-1d46bbcdab8e" />

I got stuck a little bit and checked deeper in my home directory using ls -a for hidden files:
<img width="562" height="39" alt="Screen Shot 2026-06-27 at 20 21 33 PM" src="https://github.com/user-attachments/assets/9b03caa5-81c6-4518-ac07-bce7b2e8c6e2" />

.sudo_as_admin_successful was an empty file.
I checked .bash_history to find clues, here is what I could understand and find:

1. the user created a reverse shell using php at /usr/bin/php
2. 

## Flags: 🏁 
user.txt - /home/dale/user.txt - THM{6Y0...}
root.txt - in progress..

---

## Key Takeaways: 🧠



---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
