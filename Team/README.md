## 🐲 Team - TryHackMe Write-up

## 📌 Overview
A beginner friendly boot2root machine, 

Target IP: 10.112.162.190

> Note: I suggest people who try this room to finish the following modules before:
> - [Nmap: The Basics](https://tryhackme.com/room/nmap)
> - [Gobuster: The Basics](https://tryhackme.com/room/gobusterthebasics) 
> - [ffuf](https://tryhackme.com/room/ffuf)
> - [File Inclusion](https://tryhackme.com/room/fileinc)
> - [Privilege Escalation Training](https://tryhackme.com/module/privilegeescalation)
---

## 1. Reconnaissance: 🔍
Used Nmap to scan the target IP with the following command:
```bash
nmap -sV -sC -p- -T5 --min-rate 1000 -A -O 10.112.162.190
```

Found the following services running:

> - 21/tcp open  ftp     vsftpd 3.0.5
> - 22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
> - 80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))

---

## 2. Reaching to the HTTP service using a browser: 🦊
Using the Firefox browser I went to the HTTP web page and it showed the default Apache service page.
I took a sip from my cup of coffee ☕️, and examined the source code for any clues.

I managed to find the following note in the header:
```http
<title>Apache2 Ubuntu Default Page: It works! If you see this add 'team.thm' to your hosts!</title>
```
<img width="1253" height="1140" alt="Screen Shot 2026-06-27 at 09 42 01 AM" src="https://github.com/user-attachments/assets/7815a2cf-ac9c-44ef-8cb5-80a30078a033" />

Following the note at header, I added the hostname "team.thm" to the IP by separating them with a TAB using:
```bash
nano /etc/hosts
```

And continued to investigate the web application by looking for the newly added URL:
```URL
http://team.thm
```

The following page was loaded:
<img width="2056" height="1059" alt="Screen Shot 2026-06-27 at 12 50 03 PM" src="https://github.com/user-attachments/assets/1a454eb8-8710-4983-a308-d2f53c9fedc3" />

No further information was discovered while searching the source code. I moved on to enumerating with gobuster.

---

## 3. Enumeration with Gobuster: 🔎
I used the following command to check for any directories, ".txt" files and ".php" files:


```bash
gobuster dir -u 'http://team.thm' -w /usr/share/wordlists/dirb/big.txt -x .txt,.php -t 64
```


I got the following results:
<img width="1314" height="767" alt="Screen Shot 2026-06-27 at 13 01 41 PM" src="https://github.com/user-attachments/assets/35797d39-d74c-4938-952e-5c2da706db7d" />


When checking the contents of "robots.txt" I found it had the following string in it:

> "dave"

I figured it might be some user of the system. I tried accessing them manually but didn't have access to /scripts and /assets, so I used gobuster to enumerate them too:

/scripts:
<img width="1693" height="991" alt="Screen Shot 2026-06-27 at 13 04 06 PM" src="https://github.com/user-attachments/assets/ac6f4038-aa1b-4b67-89da-fab026926c42" />
---

/assets:
<img width="1398" height="701" alt="Screen Shot 2026-06-27 at 13 05 07 PM" src="https://github.com/user-attachments/assets/72484335-f4f0-4ca8-8412-1a0e4b302efd" />
---

I wanted to check out **scripts.txt** and it had the following text in it:
<img width="1121" height="530" alt="Screen Shot 2026-06-27 at 13 07 14 PM" src="https://github.com/user-attachments/assets/79b2ed7c-4803-4b33-a0de-b666e25242b0" />

Reading this file showed me the directory has a file named "script" that had a different extension, and in this file the creds are unredacted!

---

## 4. Using FFUF to find the extension of the old "script" file: 👴🏼
Since scripts.txt referenced an older version of the script named "script" as well but didn't mention its new extension, I used FFUF with the next command to fuzz and search for the extension on 'http://team.thm/scripts' and got the following hit!

```bash
ffuf -u 'http://team.thm/scripts/script.FUZZ' -w /usr/share/wordlists/Seclists/Discovery/Web-Content/big.txt
```

<img width="1548" height="625" alt="Screen Shot 2026-06-27 at 13 13 54 PM" src="https://github.com/user-attachments/assets/eb841abe-e4f1-46df-846d-325c71ada6ad" />

The .old extension clearly indicated the old version of the referenced script file. I inspected the contents and got the following creds:
<img width="1524" height="910" alt="ffuf_scan" src="https://github.com/user-attachments/assets/27839e8e-c95b-4289-b91b-c40d6c8331c2" />

---

## 5. Connecting to the FTP service in the machine using the above creds: 🛡️
To connect to the ftp service I simply used the following format:
```bash
ftp 10.112.162.190
```
and entered the credentials from scripts.old. the service had passive mode enabled so using the "passive" command I disabled it and got to work:
<img width="1361" height="483" alt="Screen Shot 2026-06-27 at 13 26 10 PM" src="https://github.com/user-attachments/assets/93a86ba6-4da9-4e98-a647-ab225e3b7a21" />

I figured that the message talks about a subdomain within team.thm so I configured dev.team.thm as a subdomain hostname at /etc/hosts and reached the website using Firefox.

---

## 6. Viewing the website and exploiting a vulnerability: 👀
When logging into the web page at the subdomain we can see the a link that transfers us to:
> http://dev.team.thm/script.php?page=teamshare.php

I saw the "?page=" with a file after it and tried checking for LFI by replacing "teamshare.php" with "/etc/passwd" to kill 2 birds with one stone. verify a suspicious LFI vulnerability and enumerate valid local users. I managed to confirm the LFI vulnerability and was given the contents of /etc/passwd.

I wanted to filter the names of the users in the system so I used the terminal with the command:
```bash
curl 'http://dev.team.thm/script.php?page=/etc/passwd' | grep /bin/bash
```

and got a hit on:
- root
- dale
- gyles

---

## 7. Fuzzing ?page= for interesting files: 📁
I used FFUF and seclists to find interesting files that I could access. I filtered the results for ones that are bigger in size than "1" using the following command:

```bash
ffuf -u 'http://dev.team.thm/script.php?page=FUZZ' -w wordlists/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt -t 64 -fs 1
```
results are in [outputs/ffuf.results](outputs/ffuf.results).

I looked at the files and discovered something interesting at /etc/ssh/sshd_config. remember Gyles said to Dale: "make a copy of your "id_rsa" and place this in the relevent config file."? Well, he did.

it was there:

<img width="439" height="514" alt="Screen Shot 2026-06-27 at 19 34 43 PM" src="https://github.com/user-attachments/assets/44f2b2a6-495d-400a-acbc-915202d19192" />

since it was commented with "#" I used Cyberchef to replace the "#" with nothing:

<img width="1403" height="997" alt="Screen Shot 2026-06-27 at 19 37 43 PM" src="https://github.com/user-attachments/assets/11befe9e-1e80-47b1-817c-4abacd017c9d" />

I saved the key using:
```bash
leafpad id_rsa
```

With both the username and private key available, I attempted to connect to the target machine using SSH.

---

## 8. Connecting using SSH: 🔐
(For context's sake, I paused here and the machine turned off. I restarted it and it changed it's IP to 10.112.174.79)
I had an error saying the key is not protected because its permissions should only allow me to use it. so I changed the permissions to 600 using:

```bash
chmod 600 id_rsa
```

and it worked!

<img width="803" height="326" alt="Screen Shot 2026-06-27 at 19 48 24 PM" src="https://github.com/user-attachments/assets/efd682b6-2143-4f31-88b9-07d6bf013d61" />

---

## 9. Privilege Escalation: 🧗🏼‍♂️
I wanted to know what commands I can use sudo for and discovered : "/home/gyles/admin_checks"
I Analyzed the script for vulnerabilities  and found it takes ANY error from the date stamp and directly executes it.

I wanted to manipulate it to get a shell as gyles.

I used the date stamp input to run a bash shell and was given an option to run a command. I generated an interactive shell using python with:
```python
python3 -c "import pty; pty.spawn('/bin/bash')"
```

and was given gyles's shell!
<img width="1178" height="836" alt="Screen Shot 2026-06-27 at 20 00 33 PM" src="https://github.com/user-attachments/assets/1c94dfb7-b377-4277-b0d2-b5feff9b71ed" />

---

## 10. Privilege Escalation to Root 🔝
I tried getting to root but didn't have the permissions needed. I tried to check for sudo commands but needed a password so I skipped. I checked for running processes with "ps aux" but the processes were cut out:

<img width="919" height="1084" alt="Screen Shot 2026-06-27 at 20 06 08 PM" src="https://github.com/user-attachments/assets/e21ba4ae-bad7-4f44-b982-bddd5027c5c5" />

I used "ps auxww" after checking how to expand it and didn't find something useful.

I checked "journalctl" to see if there was any recent activity by root that I may be able to manipulate. nothing found yet.

I tried checking with crontab for any root activity and didn't find any for mine or root.
<img width="799" height="513" alt="Screen Shot 2026-06-27 at 20 19 18 PM" src="https://github.com/user-attachments/assets/98edf13e-9aec-49da-b1b7-19099b02e2b5" />

I then tried checking specifically for scheduled tasks in the /var/log/syslog using:

```bash
grep -i cron /var/log/syslog
```

Nothing.

<img width="562" height="39" alt="Screen Shot 2026-06-27 at 20 21 33 PM" src="https://github.com/user-attachments/assets/5c49b3a0-b5c8-4e5a-90e6-1d46bbcdab8e" />


I couldn't find any low-hanging fruits with the common privilege escalation so I looked for less obvious indicators. I checked in my home directory using ls -a for hidden files and found a few files:
(screenshot was not taken).
I began checking for .sudo_as_admin_successful for it's contents but it was an empty file.
I read .bash_history to find clues to something I can use to escalate my privileges with and gain information on the actions taken on the system, here is what I could understand and find:
1. the user created a reverse shell using php at /usr/bin/php
2. he created scripts at the following paths:
> - /usr/local/bin/main_backup.sh 
> - /opt/admin_stuff/./script.sh
> - /usr/local/sbin/dev.backup.sh
3. He gave permissions to his group to edit /opt/admin_stuff

I looked into /opt/admin_stuff and found the script.sh:

<img width="567" height="262" alt="צילום מסך 2026-06-28 ב-9 20 15" src="https://github.com/user-attachments/assets/46db0a14-3891-40bd-af2c-a334558fadac" />

So now I know main_backup.sh and dev.backup.sh runs automatically every minute due to the cronjob but I don't know by who. using ps auxww didn't help catching the process so I looked for a tool that could help me list all the processes and scripts running on the machine WITHOUT root access. I stumbled across pspy. I looked for a training related to it and found one at [Privelege Escalation Training](https://tryhackme.com/module/privilegeescalation) and I hadn't studied it yet so I took a break and learned it.

---

## 11. Using Pspy to  main_backup.sh: 🫆
I downloaded the pspy64 file, created a python HTTP server, transferred the tool to the target machine, gave it executing privileges and ran it in the system.
<img width="1713" height="427" alt="צילום מסך 2026-06-28 ב-9 53 50" src="https://github.com/user-attachments/assets/c99dc0f4-5f70-4f04-91e3-ef2151fe0512" />
I found that **UID=0 (=root) runs "main_backup.sh"**.

I checked if I could inject it with a bash reverse shell and basically manipulate the process running by root to create a backdoor for me every minute and by that gain the ability to access the system as root.

<img width="963" height="583" alt="צילום מסך 2026-06-28 ב-9 59 54" src="https://github.com/user-attachments/assets/97baeaf6-953d-4a71-bbbf-578bf0bb8253" />

I created a listener using:
```bash
nc -lvnp 9001
```

and we got the root access!

---

## Flags: 🏁 
- user.txt - /home/dale/user.txt - THM{6Y0...}
- root.txt - /root/root.txt - THM{fhq...}

---

## Key Takeaways: 🧠
1. Giving root access to a simple process like copying a file and pasting it in a different folder was proven to be a mistake. especially if not only the root is able to edit the cronjob's script.
2. pspy was proven to be an efficient tool to capture processes and cronjobs that aren't always easy to find using ps. 
3. Taking breaks helped during long rooms helped me stay calm and helped me think outside of the box.

---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
