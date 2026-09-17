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
gobuster dir -u `http://olympus.thm` -w ~/wordlists/dirb/common.txt
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
3. The machine is related to the greek mythology. If neeeded, I will be able to create a wordlist using either LLM or a script to pull from `relatedwords.com`.
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

I checked for the instructions in the attached exploit link and it basically said to upload a payload and use `sqlmap` to find the payload and manipulate on it.
