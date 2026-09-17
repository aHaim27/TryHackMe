## [TryHackMe | Olympus ⚡](https://tryhackme.com/room/olympusroom) 

- Target Machine: 10.114.151.214

<img width="735" height="134" alt="image" src="https://github.com/user-attachments/assets/47ca259f-9120-4d72-b67e-ef658ac6db79" />

--- 

## 1. Nmap Reconnaissance: 👁️
There was no information about the machine in the bio of the room so the first step I took was scanning for open ports and services on the machine using Nmap.

The command I used was:

```bash
nmap -A -T4 -o outputs/nmap_result.txt 10.114.151.214
```

You can check the result by clicking [here](outputs/nmap_result.txt)

It basically showed 2 open ports:
- port 22 - ssh
- port 80 - http that redirects to the address `http://olympus.thm`

I didn't have any credentials so I wanted to access the web application on the given URL. I added it to `/etc/hosts` and used Firefox to access it.

---

## 2. Web application reconnaissance: 🌐

I tried to access the web application using Firefox and got access to the following landing page:

<img width="960" height="540" alt="olympus-website" src="https://github.com/user-attachments/assets/1050bb59-0297-449a-b481-57ad718f4193" />

I figured that the message implies a vhost of some sort so I used `gobuster vhost` with a common wordlist and couldn't make anything stick.

---

I then moved to enumerating the website using `gobuster dir` with a common list and got a few hits, you can check the results [here](outputs/gobuster_dir_result.txt)

The command I used was:

```bash
gobuster dir -u http://olympus.thm -w ~/wordlists/dirb/common.txt
```

The one I wanted to check first was `/~webmaster` since it was the most unusual to me.

I checked the website and got the following page:

<img width="960" height="540" alt="webmaster" src="https://github.com/user-attachments/assets/0e2eecec-6372-41bc-8b06-320636058ba5" />

I looked around the web application. It had a couple of posts talking about insecure user's passwords and had a search bar and login input.

I then stopped to write down all the information I had until now to summarize the reconnaissance to this point.

---

## Summarize to this point: ✍️

1. The machine has a web application on port 80 using http protocol and redirects a user to a site on the URL `http://olympus.thm`
2. The machine also has the ssh service open on port 22. I need to find credentials to use it.
3. The machine is related to the greek mythology. If needed, I will be able to create a wordlist using either LLM or a script to pull from `relatedwords.com`.
4. The web application on the machine has a page on `/~webmaster` regarding posts related to weak credentials on a user and has the ability to use a search bar and login creds input.
5. The web application has a string saying `"Victor's CMS"` on the header of the page.
6. There is a user named `root` on the machine that posted 2 posts.

---

## 3. Further reconnaissance: 📝

I checked the search bar and the login input for any easy exploits by checking how the packet is being transferred and could use the login prompt with `hydra` but I didn't have any username yet.

I tried opening a few more links in the website and saw something that reminded me of a LFI vulnerability but I couldn't get it to stick as well.

I then tried searching about `Victor's CMS` and found that it is a VERY vulnerable web engine.

---

## 4. Victor's CMS vulnerability assessment: 🕵🏼

I looked at `Exploit Database Search` and found a couple of vulnerabilities. The one that caught my eye that I wanted to try first was the [Victor CMS 1.0 - 'Search' SQL Injection](https://www.exploit-db.com/exploits/48734) because I wanted to check if the search bar I found earlier was exploitable.

I checked for the instructions in the attached exploit link and it basically said to use `sqlmap` on the vulnerable search parameter that is being sent as:

```bash
search="[SQLi]"&submit
```

I used `sqlmap` using the exploit's given command, configured it to my needs, and let it run and dump the databases:

```bash
sqlmap -u "http://olympus.thm/~webmaster/search.php" --data="search=1337*&submit=" --dbs --random-agent -v 3
```

I was given 6 databases named:
- information_schema - metadata related to the databases
- mysql - information related to the actual software
- olympus - Unknown -> Chose this one to look inside first
- performance_schema - performance-related information
- phpmyadmin - Unknown -> will go to that second
- sys - more performance-related information

as I mentioned above, I started by checking the `olympus` database and checked for it's tables with the following command:

```bash
sqlmap -u "http://olympus.thm/~webmaster/search.php" --data="search=1337*&submit=" -D olympus --tables --random-agent -v 3
```

and got the following 6 tables:
- categories -> showed categories on the website.
- chats -> Unknown -> checked third 3️⃣
- comments -> showed comments on the.
- flag -> Flag 1! -> checked first 1️⃣
- posts -> root's posts on the webpage
- users -> Users information -> checked second 2️⃣

---

## 5. Using Olympus's tables information: 💻

We have two tables we want to check. The first is `users` because it may contain login credentials and the second is `chats` because it is something unknown which may show us hints, ideas of where to search next, users etc...

first, we will go over `users`
the table `users` shows a table with user_names, user_roles, user_emails, user_passwords, user_firstnames for 3 users:
1. prometheus
2. root
3. zeus

the passwords are hashed to use them we need to crack them. I copied the hashed passwords to a file and chose to use `hashcat` because it uses my RTX 3070's power which is most of the time faster then my CPU. I checked what the type of hash by going to hashcat's [example_hashes (hashcat wiki)](https://hashcat.net/wiki/doku.php?id=example_hashes) and found the following hash as the most similar. I tried filtering for `$2y` and got nothing so I removed the letter "y" and got this following hit:

<img width="903" height="29" alt="Screenshot 2026-09-17 181547" src="https://github.com/user-attachments/assets/22163b3d-9998-40c8-af6a-5d7fe8bede8d" />


I then moved the file to my Windows machine from my Kali VM and used the following command:

```bash
hashcat.exe -m 3200 .../hashed_passwords.txt .../wordlists/rockyou.txt
```

after a while I saw it might take me *over 8 hours* but I saw I already managed to crack one of the hashes so I stopped the cracking and used the `--show` flag and saw I have prometheus's password cracked.

<img width="856" height="543" alt="Screenshot 2026-09-17 182300" src="https://github.com/user-attachments/assets/ea5645fc-1ec3-4216-a098-6411ed5d784c" />

---

While cracking the password, I checked the `chats` table that contained a chat between `prometheus` and `zeus` where prometheus uploaded a file named `"prometheus_password.txt"` and `zeus` explains `prometheus` that the file's name is salted. but inside the table I can see the .txt's new salted name which is:

`47c3210d51761686f3af40a875eeaaea.txt`

I tried accessing it but couldn't reach it.

---

By this point I had credentials for prometheus anyways so I moved to login with them to the website

---

## 6. Using prometheus's credentials to enumerate: 🔍

I signed into the website using prometheus's account and got into the `CMS admin page` and looked for other known vulnerabilities I could use using my current privileges.

I tried using [Victor CMS 1.0 - Authenticated Arbitrary File Upload](https://www.exploit-db.com/exploits/48490) which uses a vulnerable `GET parameter '/admin/users.php?source=add_user'` but I when using it I didn't have access to the `/img` folder and my file.

I kept digging and went to the users page and saw the users table from earlier and saw the email root and zeus have are related to some sort of sub-domain named `chat.olympus.thm` which I couldn't get using `gobuster vhost` from earlier.

I could swear the wordlist included the word "chat". I investigated further and with the help of an LLM I managed to understand where the point of failure was.

With my initial VHost enumeration, the status code and response size did not distinguish `chat.olympus.thm` from invalid hosts. Manual comparison revealed that the `Location` header was different.

<img width="688" height="164" alt="image" src="https://github.com/user-attachments/assets/1140fb9c-d056-4199-a2ed-8cb8efaf81fc" />

I wanted to scan for more sub-domains using by filtering the location parameter and used ChatGPT to create a script that will enumerate the sub-domains based on my desired filter.

The script:

- Reads candidates from a SecLists subdomain wordlist (which contains less false-positives then dirb/common.txt).
- Sends multiple requests concurrently.
- Modifies the HTTP `Host` header for each candidate.
- Uses the default redirect as a baseline.
- Displays only responses that deviate from that baseline.
- Tracks the scan progress.

You can use it yourself by copying the content or downloading it and running it on your Linux machine [here](scripts/vhost_enum.sh).

The script did not identify any additional VHosts from this wordlist, so I moved on to adding `chat.olympus.thm` to the `/etc/hosts` file and accessed the web application.

---

## 7. Accessing chat.olympus.thm: 🗨️

<img width="695" height="556" alt="image" src="https://github.com/user-attachments/assets/0b989095-c960-43ac-9f43-0b090ebc3f25" />

The login page had a username and password input so I used prometheus's creds and signed in. I was greeted by the following page:

<img width="1001" height="938" alt="image" src="https://github.com/user-attachments/assets/edd96481-c2ec-451a-b4c1-715205c83322" />

I tried accessing the `prometheus_password.txt` file from earlier using the hashed new name but the file wasn't uploaded to the current directory. I used `gobuster` again for directory enumeration using the following command:

```bash
gobuster dir -u 'http://chat.olympus.thm' -w wordlists/dirbuster/directory-list-2.3-small.txt
```

the results of the scan can be viewed [here](outputs/gobuster_2nd_dir_result.txt)

I found there was an `/upload` folder and I used it to access the file and got a hit!

<img width="915" height="137" alt="image" src="https://github.com/user-attachments/assets/2bf1dc73-c45f-430a-abe9-71a74db3c4ab" />

---

I stopped here for a quick summary:
1. I now have access to prometheus's creds on the web application
2. I found an interface where I can upload files and access the via the `/uploads` sub-directory.
3. Any file I will upload will have it's name changed so I will need to find the file's new name using the same SQLi method I used earlier.

My current new current goal:

1. Get access to the machine's file system using a shell interface with basic privileges
2. After getting basic privileges, understand how to escalate my privileges.

---

## 8. Getting shell interface: 🐚

I wanted to create a reverse shell to the machine using a `.php` file. I didn't know if there's any filter for what type of file I can upload or view but I tried to check if it works anyway. I opened a `nc` listener and created a `.php` reverse shell command and uploaded it to the chat. The command I used is a `PHP PentestMonkey` for it's better stability. you can view it [here](scripts/revshell.php)

I then used `sqlmap` to show me a fresh view of the table `"chats"` and I was able to find the `.php` file I uploaded with it's new name. The command I used is:

```bash
sqlmap -u "http://olympus.thm/~webmaster/search.php" --data="search=1337*&submit=" -D olympus -T chats --dump --fresh --random-agent -v 3
```

I then accessed the file in the `/uploads` folder the same way I accessed `prometheus_password.txt` and got a shell!

<img width="1263" height="270" alt="image" src="https://github.com/user-attachments/assets/451b314c-efef-4bfb-9f85-bc81f174ed6e" />

I looked for the users in the system and found `"zeus"` and in his home directory I found the second flag of the room

<img width="545" height="252" alt="Screenshot 2026-09-17 201152" src="https://github.com/user-attachments/assets/54b1afa7-a236-4014-93bc-8a6cb9d11081" />

---

## 9. Privilege escalation: 👑

I opened the file `"zeus.txt"` in zeus's home directory and found a message from Prometheus:

<img width="644" height="248" alt="image" src="https://github.com/user-attachments/assets/73767d8e-286f-41fe-8e9f-afb0bf74f919" />

I figured that if prometheus has some way of accessing the machine with super-user privileges, I need to find where his backdoor is.

I searched for applications with the SUID bit set that I could potentially abuse to execute actions with elevated privileges using:

```bash
find / -perm -4000 -type f 2>/dev/null
```

I found I can use a binary called `cputils` which I wasn't familiar with. I searched it on Google and found the following information:

<img width="584" height="90" alt="image" src="https://github.com/user-attachments/assets/ad67ca9a-e860-45eb-8c87-3a24e28591f3" />

In short, I potentially had access to copy any file I want on the system.

I tried copying 2 files and understood I might lack the needed privileges:

<img width="498" height="437" alt="image" src="https://github.com/user-attachments/assets/c3dd26fc-1ee6-40f0-aeba-0558358df03e" />

I stopped to think about what I want my following steps to be.

---

Here is what I knew so far:
1. I knew I wanted to gain a shell to the system in order to look around the file system.
2. My initial copy attempts failed, so I still did not fully understand what cputils could access.
3. I knew there is a backdoor running which allows prometheus to have super-user privileges but I didn't know where or what the name of the backdoor might be.
4. I knew there are 2 services running: http and ssh.

After some thought I got to a conclusion that I want to give more time to enumeration on the file system with my current privileges and to not try yet to escalate my privileges.

I divided the filesystem enumeration into two areas of interest: user data and web application files.
1. The files of the users on the machine (regarding the ssh service)-> which I felt like I exhausted the mapping of with my current privileges.
2. The files of the http service (regarding the http service) -> which I didn't actually look at yet.

---

I went to `/var/www/html` and found an irregular folder called `0aB44fdS3eDnLkpsz3deGv8TttR4sc`

I didn't have privileges to open it but zeus did.

<img width="806" height="157" alt="image" src="https://github.com/user-attachments/assets/3ea96bb3-bd63-47ec-a462-c3a6925263df" />

I wanted to gain access to zeus's account to get inside that folder. I checked his home directory again and noticed he has a `.ssh` directory which may imply he has an id_rsa there I might be able to copy using CPutil. (I couldn't use `cat` on it because I didn't have sufficient privileges.)

After trying to get inside the `.ssh` folder, I tried copying the file from outside of it on `/home/zeus` and got CPutils to copy the `id_rsa` successfully.

I copied the content of the id_rsa and used it to connect to the machine but got asked for a passphrase:

<img width="802" height="1111" alt="image" src="https://github.com/user-attachments/assets/453424a2-0d70-4b7e-815c-a761fece4444" />

I used `john` to crack it using rockyou.txt and got the passphrase:

<img width="931" height="269" alt="Screenshot 2026-09-17 211436" src="https://github.com/user-attachments/assets/9f457beb-dfca-44b5-b8df-23d5e2e92a93" />

---

<img width="713" height="681" alt="image" src="https://github.com/user-attachments/assets/a96dbb22-3a6d-4151-a878-734a5aad7c51" />

---

I was now able to access `/var/www/html/0aB44fdS3eDnLkpsz3deGv8TttR4sc` and got found a suspicious `.php` file

<img width="1919" height="1130" alt="image" src="https://github.com/user-attachments/assets/15d058cb-d468-4d95-b2e7-f0fdf5a0a3f5" />

The file basically says the following thing:

- There is a backdoor binary at `/lib/defended/libc.so.99`
- The .php acts as a reverse-shell wrapper around the pre-existing SUID backdoor located at the above path.
- The .php is defended by a password shown on the header of the file.

The backdoor was stored under `/var/www/html`, which was Apache's default DocumentRoot rather than the DocumentRoot of the named `olympus.thm` or `chat.olympus.thm` VirtualHosts. Accessing the target directly by IP caused Apache to serve the default VHost, allowing me to reach the PHP file.

I used the browser to access `http://10.114.151.214/0aB44fdS3eDnLkpsz3deGv8TttR4sc/VIGQFQFMYOST.php`. After submitting the hard-coded password, the same PHP script displayed its usage instructions and requested an IP address and listener port:

<img width="1093" height="306" alt="image" src="https://github.com/user-attachments/assets/5f7d79fb-1632-4e60-895e-e299e80dcc04" />

I disconnected from my reverse shell, launched a listener to the existing backdoor and changed the IP and Port to mine and got access to `root`!:

<img width="1261" height="277" alt="Screenshot 2026-09-17 213825" src="https://github.com/user-attachments/assets/2d315068-f5fd-420f-9532-70cd5c4ee563" />

I used `ls /root` and found the third flag!

I couldn't get to see the entire flag so I moved it to `/var/www/html` and looked at it from a browser:

<img width="795" height="839" alt="Screenshot 2026-09-17 214416" src="https://github.com/user-attachments/assets/88d83cee-5391-46d1-8f00-e899b61d722d" />

---

## 10. The bonus flag: 🏳️

to access root over ssh I created a temporary private key and added a public key to the authorized keys on the root's target machine and refreshed the permissions.

Then, I saw in the TryHackMe site a hint to the fourth flag that mentions the flag is located at `/etc`.
I searched for the string `"flag{"` and got a hit on the fourth flag

<img width="582" height="591" alt="Screenshot 2026-09-17 220044" src="https://github.com/user-attachments/assets/5695f482-c553-4e6c-8fe7-0e0ed21b8357" />

---

## Key Takeaways 🧠

1. **Enumeration is a continuous process, not a one-time step at the beginning of an assessment.**  
   Olympus contained information scattered across the web application, database, filesystem, user accounts, and configuration. Every new finding created another enumeration opportunity.

2. **Default tool output should always be validated when something does not make sense.**  
   My initial VHost enumeration did not reveal `chat.olympus.thm`. By manually comparing responses, I discovered that the useful difference was in the `Location` header and built a small script to enumerate based on that behavior.

3. **A vulnerability can provide more than one type of information and can often be chained with other weaknesses.**  
   The SQL injection was initially useful for database enumeration, but I later reused it to recover renamed upload filenames. Combining information from multiple weaknesses was essential to progressing through the room.

4. **You do not always need to fully exhaust one path before using the information it already provided.**  
   Cracking a single useful bcrypt password was enough to continue the attack path, so waiting several additional hours for every remaining hash would not have provided immediate value.

---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
