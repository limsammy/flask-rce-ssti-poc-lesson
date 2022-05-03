# Lesson: Remote Code Execution (RCE) via Server-Side Template Injection

## 0 - Preface

### Clarifying Naming Discrepencies

So, what is exactly is a *Remote Code Execution* vulnerability?

Before continuing, it is important to clarify some naming discrepencies that may cause confusion. *Remote Code Execution*, often referred to by it's acronym, *RCE*, is commonly known and referred to by several other (similar) terms; *Arbitrary Code Execution* (*ACE*), as well as the more generalized term, *Code Injection*.

While minor differences do exist between the various terminology, they are somewhat minute in the scope of this lesson.

To briefly touch on the minor differences between an *RCE* attack and an *ACE* attack:

* **Remote Code Execution:** This terminology infers that an attacker can exploit a vulnerability to trigger arbitrary code execution *from a remote system* on the target application. These attacks are typically conducted via the internet, WAN, or LAN.
* **Arbitrary Code Execution:** In contrast to aforementioned *remote code execution*, this terminology infers that an attacker can exploit a vulnerability to trigger *any code* execution on the target application.

> *Note that ACE excludes the term "remote" from it's phrasing, as it does not specify the origin of the code being executed. However generally speaking, arbitrary code execution will often leverage remote code execution, as well as the local code implementation of the application(s) running on the target system.*

Lastly, *Code Injection* is somewhat of an umbrella term that encompasses both *Remote Code Execution* and *Arbitrary Code Execution* vulnerabilities.

### Server-Side Template Injection

While not directly in the scope of the definition of a remote code execution vulnerability, this lesson will cover an extremely common attack vector used to *establish* an RCE: Server-Side Template Injection

Server-side template injection is when an attacker is able to use native template syntax to inject a malicious payload into a template, which is then executed server-side. It is enormously common for web applications to use a template engine to dynamically render data from the backend in the user-facing HTML.

> Template engines are designed to generate web pages by combining fixed templates with volatile data. Server-side template injection attacks can occur when user input is concatenated directly into a template, rather than passed in as data. This allows attackers to inject arbitrary template directives in order to manipulate the template engine, often enabling them to take complete control of the server. As the name suggests, server-side template injection payloads are delivered and evaluated server-side, potentially making them much more dangerous than a typical client-side template injection.
>
> &mdash; PortSwigger, [Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)

## 1 - Intro

### Description

Most commonly, Remote Code Execution vulnerabilities presents themselves due to lack of proper input/output validation. A threat actor can achieve RCE using a variety of methods and techniques. The following are two examples of such techniques (of which, the former will be the focus of this lesson):

* **Injection Attacks:** Many applications, especially user-facing web applications, use user-provided data as input for a command. An extremely common example of an injection attack vector can be seen in SQL queries: The attacker deliberately provides malformed input (e.g. using the double-dash sequence `--`, which is the comment operator in SQL, to escape the query string) to be interpreted as part of the command.
* **Deserialization Attacks:** Applications and APIs commonly use [serialization](https://en.wikipedia.org/wiki/Serialization) to encode (or more accurately, *to serialize*) pieces of data into a single string for frontend/backend communication. In this case, an attacker can deliberately craft a malicious and specially formatted string for user input. The serialized input data may then be interpreted as executable code during the deserialization process.

### Impacts

Remote code execution is widely regarded as one of the most critical vulnerabilities that can be found in an application. It can leave the application, infrastructure, users, and the targeted organization/entity itself at a *very* high-risk, resulting in impacts on confidentiality, data integrity, and even business operations. For example, a threat actor in Russia could silently place malicious code on a targeted device in the United States via an RCE vulnerability.

Some of the main impacts of an RCE attack include (but are not limited to):

* **Initial Access:** RCE attacks often begin as a vulnerability in public-facing applications, granting an attacker the ability to gain an initial foothold on a device to install malware or achieve similar goals. Once the initial foothold has been established, the attacker may then begin to try and compromise the underlying system, pivot to machines within the network, attempt to infect/phish users, etc.
* **Information Disclosure:** RCE attacks can be used to exfiltrate data from the vulnerable application. Often [personally identifiable information (PII)](https://www.dhs.gov/privacy-training/what-personally-identifiable-information) such as usernames, emails, passwords, credit card numbers, social security numbers, and anything else an application may store in it's database(s). Attackers may also target information that may give further access to the underlying systems, such as API/DB credentials, internal URI's, and other critical information.
* **Denial of Service:** Given the nature of an RCE vulnerability allowing an attacker to run code on the underlying system of the target application, this can allow them to disrupt operations of the application or other services running on the system.
* **Cryptomining:** This is a specific type of malware that leverages the computational resources of a compromised system (or network of systems) to mine cryptocurrency. Given the resources needed for cryptocurrency mining, these attacks will likely impact operations, latency, and a massive increase in billing.
* **Ransomware:** [Ransomware attacks](https://www.checkpoint.com/cyber-hub/threat-prevention/ransomware/) began gaining traction after the [WannaCry](https://en.wikipedia.org/wiki/WannaCry_ransomware_attack) outbreak of 2017. This variety of malware aims for complete takeover of compromised systems via infection and distribution vectors (RCE's, phishing emails, etc.). Once the ransomware has gained access to a system, it begins an encryption routine of all filesystems. After all files and data have been encrypted, a ransom demand is made in exchange for the decryption key, often with a time limit set before destroying the filesystems and/or leaking all data publically. This can often be devestating to organizations of any size.

## 2 - Vulnerabilty and Exploitation

Next, let's take a look at what an RCE vulnerability and exploitation may look like in the wild.

For this example, we will be utilizing Python's [Flask web framework](https://flask.palletsprojects.com/en/2.1.x/) to serve dynamic HTML pages using the [Jinja2 templating engine](https://jinja.palletsprojects.com/en/3.1.x/), commonly used in most Python web applications, including Flask and Django. Our example will make use of a technique known as [server-side template injection](https://portswigger.net/research/server-side-template-injection) to exploit a critical remote code execution vulnerability.


### Establishing the Demo Code

Before proceeding let's write some code for a basic web application served via Flask, that renders a Jinja2 template.

In an example file called `app.py`, let's write an extremely basic Flask app. We will establish a controller that will handle any GET requests to the index route, `/`. Additionally, we will check for query args attached to the request context via `request.args`, and if it exists, we will render a different template string.

```python
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    name = request.args.get("name") or None
    if name:
        template = (
            """<p> Hello, %s 
        """
            % name
        )

    else:
        template = """
        <p> What yor name? </p>
        <form method="get" action="/">
        <p>
            Enter your name:
            <input type="text" name="name">
        </p>
        <input type="submit" value="Submit">
        </form>"""

    return render_template_string(template, name=name)
```

### What is a template?

In simple words, it is an HTML file that contains variables. For example:

```html
<p>Hello, {{ name }}!</p>
```

With Jinja2, variables are defined using `{{ }}`. These variables are assigned in the backend (Flask app), which are then passed to the template.

If we set `name = "admin"` in our Flask controller function, then the HTML rendered would be:

```html
<p>Hello, admin!</p>
```

So, to recap: Templates are used by the backend app to render data dynamically into HTML.

### What is server-side template injection?

We briefly covered this in the intro, but let's touch on it again. 

**If an application blindly accepts user input (such as `name`) and renders it into a template, then an attacker can pass arbitrary code which the template will evaluate.**

This approach will allow the attacker to access various APIs and methods which they are not supposed to.

### Reconaissance

Server-side template injection vulnerabilities often go unnoticed *not because they are complex*, but because they are only really apparent to auditors/reviewers explicitly looking for them. Thus, an attacker will usually attempt to discover the vulnerability manually, with trial and error.

The first step is to identify the type of template engine the application is using. We already know that our demo application is using Jinja2, but for the sake of the explanation, let us assume the template engine is unknown. A common approach for detecting the template engine is to try [fuzzing](https://owasp.org/www-community/Fuzzing) the template by passing a sequence of special characters commonly used in template expressions, such as `${{<%[%'"}}%\`. If an exception is raised, or unexpected output is observed, this can be an indication that a server-side template injection vulnerability may exist.

Portswigger's Web Security Academy article on [Server-side template injection](https://portswigger.net/web-security/server-side-template-injection#constructing-a-server-side-template-injection-attack) goes into *much* more detail on the construction of such an attack, including detection, determining context, identification, and exploitation. It provides an extensive approach to spot the vulnerability with different template types.

So for this lesson, we can attempt to pass `{{ 7*7 }}` as the `name` variable to our example application. If we navigate to `http://127.0.0.1:5000/`, the following is rendered:

```html
<p>Hello, 49</p>
```

With that output, we can conclude that the application accepted our input and *evaluated* the `7*7` operation, meaning the application is vulnerable to server-side template injection.

This is a very basic example of remote code execution! We've successfully determined that we can pass code via the input form and it will be evaluated on the controller side :-)

### How is this exploitable?

After identifying the server-side template injection vulnerability, then what?

We can assume that the template evaluation happens on the server-side. This means that if we can somehow devise a weaponized input to force the template to access the underlying operating system, we can compromise the server.

We've taken a look at how to identify such vulnerabilities, so now we should look at potential payloads we can construct to establish a foothold. [Here](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/README.md#jinja2) is a very good page for all-things-template-injection. If we take a look at the Jinja2 section, we can find the necessary examples to establish a [reverse shell](https://www.acunetix.com/blog/web-security-zone/what-is-reverse-shell/) using `netcat` to listen on a local port, and send a payload through the vulnerable input form to connect to our listener.

[Here](https://podalirius.net/en/articles/python-vulnerabilities-code-execution-in-jinja-templates/) is a great writeup on the subject that goes into detail on constructing the payload using various enumeration methods.

### How do we fix this

For most webframeworks, it is mostly handled for you. However any engineer should be aware of how threat actors *do* find these vulnerabilities. One of, if not the most, important aspect of handling user input is *validation*. Input validation (eg. rejecting/escaping special characters and limiting user input to alphanumerical, and additionally typecasting all inputs to strings), One of the simplest methodologies for ensuring secure template rendering is ensuring logic is properly separated from the view and controller. Another measure is to only execute user input in a sandbox environment, where potentially dangerous modules and functions have been removed or disabled altogether. Unfortunately, as [Portswigger](https://portswigger.net/web-security/server-side-template-injection) so eloquently puts it, *sandboxing untrusted code is inherently difficult and prone to bypasses.*. 

Lastly, be sure to utilize whichever framework(s) built-in functions that handle unsafe inputs. For example, Flask's `render_template` will autoescape strings. Template injection extends far beyond RCE's, and can be used for XSS attacks and much more.
