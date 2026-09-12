## TryHackMe | Lo-Fi 🎧🎵
- Want to hear some lo-fi beats, to relax or study to? We've got you covered!
<img width="769" height="260" alt="Screenshot 2026-09-12 200704" src="https://github.com/user-attachments/assets/733a4819-7433-40bd-a3b4-01c1c12ccb2a" />

Target IP: 10.113.161.76
Referred rooms:
* [LFI Path Traversal](https://tryhackme.com/r/room/filepathtraversal)
* [File Inclusion](https://tryhackme.com/room/fileinc)

---

## Initial thoughts from the overview: 🧠
The task above requests the usage of exploiting LFI vulnerabilities to gain access to the root directory and find the flag there.

---

## Step 1 - Nmap scan: 👁️
I began by scanning the open ports on the system.
result can be found in the outputs folder or by [Clicking here](outputs/nmap_scan)

port 22 and port 80 were open.

---

## Step 2 - Checking the web interface 🌐
When I opened the web interface I had the following site in front of me:
<img width="960" height="540" alt="Screenshot 2026-09-12 195637" src="https://github.com/user-attachments/assets/60a483f6-1062-48d1-8ffe-a842c42177a8" />

I started clicking on the links on the right and saw the address change to "?page=..."
<img width="960" height="540" alt="Screenshot 2026-09-12 195655" src="https://github.com/user-attachments/assets/44bf06e9-6d4f-4549-8237-0198caddee04" />

I checked if I could get access to the /etc/passwd content and got a pleasing message:
<img width="960" height="540" alt="Screenshot 2026-09-12 195712" src="https://github.com/user-attachments/assets/95b33b2d-95cb-4b55-be92-8287aed9bfec" />

---

## Step 3 - Fuzzing for LFI: 📂
I used FFUF with the following command to check for LFI vulnerabilities:
* note: I filtered the number of lines to anything other than results that have 124 lines because on the source code of the error page there are 124 lines.
``` bash
ffuf -w /usr/share/wordlists/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -u "http://10.113.161.76/?page=FUZZ" -fl 124
```

<img width="960" height="540" alt="Screenshot 2026-09-12 195947" src="https://github.com/user-attachments/assets/bf156913-8bce-4ee3-b844-ce55a8bfaa2c" />

I was able to access /etc/passwd using a directory traversal sequence three times ("../")

---
## Step 4 - Fuzzing the root directory: 🔓
I then proceeded to fuzz the root directory for the flag (as mentioned in the task):
* note: this time I filtered by number of words because errors were shown with 1,367 words
```bash
ffuf -w /usr/share/wordlists/dirb/common.txt -u "http://10.113.161.76/?page=../../../FUZZ" -e .txt,.php -fw 1367
```

<img width="960" height="540" alt="Screenshot 2026-09-12 200401" src="https://github.com/user-attachments/assets/27259a53-492b-4133-b398-f5f183ec9209" />

---
## Final step - Getting the flag! 🏳️
I found a file named "flag.txt" in the root directory and used curl to print the source code of the web page and used grep to filter the flag and finished the task:
```bash
curl "http://10.113.161.76/?page=../../../flag.txt" | grep "flag"
```

---
## Key Takeaways: 🔑
1. Reading the task carefully helped narrow down the search. I only needed to look in the root directory and not the entire system thanks to the task mentioning it.
2. I used FFUF to increase productivity and cut time by automating the LFI manipulation. Made it even more efficient by using filters.

---
Disclaimer: ⚠️
This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
