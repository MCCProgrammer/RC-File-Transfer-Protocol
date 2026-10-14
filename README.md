# 📁 File Transfer Protocol — Computer Networks

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-1f2328?style=flat-square&logo=python&logoColor=white">
  <img alt="Course" src="https://img.shields.io/badge/Course-Computer%20Networks%20(RC)-1f2328?style=flat-square">
  <img alt="Year" src="https://img.shields.io/badge/2025%2F26-3rd%20year%2C%201st%20semester-1f2328?style=flat-square">
</p>

Assignment 1 of *Redes de Computadores* (Computer Networks), Computer Science degree at **NOVA School of Science and Technology (FCT NOVA)**.

## About

A small **client/server file transfer protocol** over **TCP sockets**, in the spirit of TFTP. Messages are tuples with an opcode — request, data block, acknowledgement or error — and every block of up to 512 bytes must be acknowledged before the next one is sent.

- The server greets each client and serves many clients at once, **one thread per connection**.
- `dir` lists the files available on the server; `get <remote> <local>` downloads a file block by block; `end` closes the session.
- Malformed packets and missing files are handled with error messages.

## Running it

```bash
# in the folder with the files to share
python3 server.py 9000

# in another terminal
python3 client.py 127.0.0.1 9000
```

```text
Connect to server
Welcome to 127.0.0.1 file server
client>dir
notes.txt
photo.bin
client>get photo.bin photo-copy.bin
File transfer completed
client>end
Connection close, client ended
```

## What I learned

- TCP sockets, and designing a simple application-level protocol with message types and acknowledgements
- Serving concurrent clients with threads

## Authors

- **Miguel Carmo** ([@MCCProgrammer](https://github.com/MCCProgrammer))
- **Tomás Ramos Alves** ([@Alvesss04](https://github.com/Alvesss04))

---

<sub>The assignment statement is not included in this repository, as it belongs to the course's teaching staff. This is a student project shared for portfolio purposes.</sub>
