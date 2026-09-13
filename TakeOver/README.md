# TryHackMe - TakeOver 🔗 

"This challenge revolves around subdomain enumeration."

Target Machine: 10.113.136.112

<img width="745" height="164" alt="Screenshot 2026-09-13 122041" src="https://github.com/user-attachments/assets/0125af46-8c99-4c33-b74b-c99cbdae093c" />

---

## 1. Initial Enumeration
I used Nmap to perform an initial scan for open ports on the target machine. 

```bash
nmap -sCV -T4 -A -O -o active/outputs/nmap_scan 10.113.136.112
```

For the Nmap result, [Click Here](outputs/nmap_result)

#

In addition to that, I added the domain to `/etc/hosts` using the following string as mentioned in the task's information:
```text
10.113.136.112  futurevera.thm
```

---

## 2. Web Enumeration

I checked "https://futurevera.thm/" using Firefox,
The source code didn't have signs of anything irregular and neither the assests folder and the js folder.
<img width="960" height="540" alt="Screenshot 2026-09-12 234850" src="https://github.com/user-attachments/assets/a21d0bd6-47f7-4fe4-a7af-1bee7156ab55" />

The certificate was self-signed but it didn't have anything to assist me with the task.

---

## 3. Virtual Host Enumeration

After being unable to find any visible information on the website I checked for sub-domain as mentioned in the task's additional information.

I used gobuster to automate the search for any subdomains with common words.

```bash
gobuster vhost -u "https://futurevera.thm" -w /usr/share/wordlists/dirb/common.txt --append-domain -k
```

- gobuster vhost = configured gobuster to check for virtual hosts
- -u "https://futurevera.thm" = configured the URL
- -w /usr/share/wordlists/dirb/common.txt = defined the wordlist
- --append-domain = makes the domain appear AFTER the words in the wordlist
- -k = skips TLS certificate verification process.

for the gobuster results, [Click here](outputs/gobuster_result)

In short, the gobuster scan showed 2 positive results:
- `blog.futurevera.thm`
- `support.futurevera.thm`

I added them to `/etc/hosts` by appending the domains with a space as a seperator:
```text
10.113.136.112  futurevera.thm blog.futurevera.thm support.futurevera.thm
```
---

## 4. Checking the Blog sub-domain:

I checked `blog.futurevera.thm` first and like the first webpage, there was noting to see in the source code, certificate, assests, javascript etc...
<img width="960" height="540" alt="Screenshot 2026-09-12 234834" src="https://github.com/user-attachments/assets/0d4446a6-aa3c-4864-ba9d-7189a1bb52cc" />

---

## 5. Checking the Support sub-domain:
I checked the support sub-domain and found no evidence in the source code, assets & javascript folders as well but this time there was a hint in the browser
<img width="960" height="540" alt="Screenshot 2026-09-12 235049" src="https://github.com/user-attachments/assets/a656b8b1-36e0-4947-8e49-6c960b5d3d4b" />

I added the secret domain to the `/etc/hosts` and checked the website too:

---

## 6. Checking the Secret sub-domain:
I checked for the website using HTTPS and it transfered me to what seems to appear as the original website.
I checked for anything that can assist me to find vulnerabilities or clues but couldn't find any on the source code, certificate and folders.

Since there were no low-hanging fruits, I wanted to analyse the transition between my browser and the web server.
I used `curl -v` to find the header being sent and was able to locate the flag in plain text there.

---

## Key Takeaways
- At first I used FFUF to try and get the sub-domains checked but I didn't seem to get it to work. probably faulty use of flags but I quickly swithced to gobuster and managed to efficiently check for sub-domains correctly.
- When checking for website sub-domains, certifications can come in handy because sometimes additional information can be found there.
