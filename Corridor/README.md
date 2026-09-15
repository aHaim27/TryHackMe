## [TryHackMe | Corridor](https://tryhackme.com/room/corridor) 🚪

- Can you escape the Corridor?

Target Machine: 10.114.146.204

<img width="512" height="512" alt="image" src="https://github.com/user-attachments/assets/62f604f0-ec3a-43ec-a823-271af8b0be1e" />

---

## Task information: 📃

<img width="750" height="74" alt="image" src="https://github.com/user-attachments/assets/a7c89f3d-cb42-4f3f-8024-8c7a4c2448cd" />

## Base assumptions from the information above:

it seems like I am tasked to do a few things:
1. Examine the URL
2. Note the hexadecimal values (hashes?)
3. Find the hidden room using the information I have

Let's get to work!

---

## 1. Access the target web application: 🌐

I used Firefox to gain access to web application by entering the IP address in the URL.

The application displayed an image of a corridor containing several clickable doors. Clicking a door changed the URL to a hexadecimal value and showed an empty room. 

<img width="960" height="540" alt="Screenshot 2026-09-15 232432" src="https://github.com/user-attachments/assets/0eebfa3c-8ce1-4f47-9768-5f0333f44d73" />

<img width="960" height="540" alt="Screenshot 2026-09-15 232512" src="https://github.com/user-attachments/assets/62784e50-2765-40b7-bf16-bd0927e2f42d" />

---

## 2. Gather information from the website: 🤓
I opened the source code and copied all the hashes into a `hashes.txt` file I created in the terminal and stored it in my `outputs` folder.

<img width="960" height="540" alt="Screenshot 2026-09-15 232457" src="https://github.com/user-attachments/assets/8ad2dfd1-d7fa-4b15-befe-420667152b70" />

---

## 3. Identifying hash values: 🔎

I then used [Crackstation](https://crackstation.net/) which is an online hash lookup service that compares hashes against large pre-computed databases and dictionaries.

I pasted all the hashes I found into the website and found that the hashes are digits that go from 1 to 12 in MD5 format:

<img width="960" height="540" alt="Screenshot 2026-09-15 232527" src="https://github.com/user-attachments/assets/0c538bc3-2020-46c0-abb9-95843eb1c01a" />

I then generated the MD5 hash of `13` and used it in the URL.
<img width="893" height="303" alt="Screenshot 2026-09-15 232600" src="https://github.com/user-attachments/assets/17504abe-44d6-41b8-a4d8-73f39c41a8bd" />


It wasn't a successful attempt. I then tried using MD5 hashe of `0` and got the flag!

<img width="866" height="308" alt="Screenshot 2026-09-15 232546" src="https://github.com/user-attachments/assets/31b02de6-a35f-4de5-897b-5e75774189cb" />

---

## Key Takeaways: 🧠

1. I think the room's first lesson is that hashing an object ID does not replace proper authorization. Even though the object references were represented as MD5 hashes, the underlying values were predictable numbers, which made it possible to generate additional valid references.

2. Obfuscating an object identifier is NOT an effective access-control mechanism. Authorization should always be enforced on the server side, regardless of whether the identifier is a number, hash, UUID, or another value.

---

## Disclaimer: ⚠️

This work was performed in a controlled, legal lab environment provided by TryHackMe for educational purposes only.
