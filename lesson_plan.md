# Remote Code Execution (RCE) via Server-Side Template Injection

## 0 - Preface: Clarifying Naming Discrepencies

So, what is exactly is a *Remote Code Execution* vulnerability?

Before continuing, it is important to clarify some naming discrepencies that may cause confusion. *Remote Code Execution*, often referred to by it's acronym, *RCE*, is commonly known and referred to by several other (similar) terms; *Arbitrary Code Execution* (*ACE*), as well as the more generalized term, *Code Injection*.

While minor differences do exist between the various terminology, they are somewhat minute in the scope of this lesson.

To briefly touch on the minor differences between an *RCE* attack and an *ACE* attack:

* **Remote Code Execution:** This terminology infers that an attacker can exploit a vulnerability to trigger arbitrary code execution *from a remote system* on the target application. These attacks are typically conducted via the internet, WAN, or LAN.
* **Arbitrary Code Execution:** In contrast to aforementioned *remote code execution*, this terminology infers that an attacker can exploit a vulnerability to trigger *any code* execution on the target application.

> *Note that ACE excludes the term "remote" from it's phrasing, as it does not specify the origin of the code being executed. However generally speaking, arbitrary code execution will often leverage remote code execution, as well as the local code implementation of the application(s) running on the target system.*

Lastly, *Code Injection* is somewhat of an umbrella term that encompasses both *Remote Code Execution* and *Arbitrary Code Execution* vulnerabilities.

## 1 - Description & Impacts

Per OWASP's article on *[Code Injection](https://owasp.org/www-community/attacks/Code_Injection)*, this attack is defined as the following:

> Code Injection is the general term for attack types which consist of injecting code that is then interpreted/executed by the application. This type of attack exploits poor handling of untrusted data.
>
> &mdash; OWASP Foundation
