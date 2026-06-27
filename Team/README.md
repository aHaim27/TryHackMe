🤡 HackPark - TryHackMe Write-up

## 📌 Overview

Target IP: 10.112.162.190


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

I figured that the message talks about a subdomain within tema.thm so I added it as hostname at /etc/hosts and checked the website.

---


## Flags: 🏁 
In progres...


---

## Key Takeaways: 🧠



---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
