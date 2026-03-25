# BD-NOT-JB

**Note : This is for dev only.**

BD-NOT-JB is RemoteJarLoader that can be used on every PS4 and PS5 fw without escaping the sandbox.  
It supports on-screen logging and network logging.  

---

RemoteLogger server is listening on port 18194.  
Use log_client.py to get the log.  
I recommend first running the log_client.py then starting the BD-J app.  

RemoteJarLoader server is listening on port 9025.  
Use jar_client.py to send the jar file.  
You can use any other TCP payload sender too.  
Don't forget to set Main-Class in manifest.txt.  

---

Use john-tornblom's **[bdj-sdk](https://github.com/john-tornblom/bdj-sdk/)** for compiling.  

---

### Credits

* **[TheFlow](https://github.com/theofficialflow)** — BD-JB documentation & native code execution sources.
* **[hammer-83](https://github.com/hammer-83)** — PS5 Remote JAR Loader reference.
* **[john-tornblom](https://github.com/john-tornblom)** — [BDJ-SDK](https://github.com/john-tornblom/bdj-sdk) used for compilation.

---


































