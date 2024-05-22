## #1 Base layer CVE monitoring
**As a** Product Owner of a team using Gardenlinux (OS / Base image) 
**I want** to register a certain version of Gardenlinux (or all packages used out of the Gardenlinux subscription), 
**So that** I want be informed if a CVE in my base layer is raised over time or already exists. 
### Acceptance Criteria  
- [ ] The user can register an installed version (either via the version like 1443.3 or a list of packages) of Gardenlinux on the GLVD page
- [ ] The registration page contains fields like "version of Gardenlinux" or "list of Gardenlinux packages" and a way to contact the user for "email" or "id for anonymous subscription"
- [ ] The user receives / is able to see a list of current CVE's in the registered Gardenlinux version / packages
### Additional Details  
**Description:**
The registration page should be accessible via a webpage. The fields for 
- "version of Gardenlinux" should allow a registration for any valid version of Gardenlinux (Notes).
- "list of Gardenlinux packages" should allow to upload a list similar to our manifest list with the columns "packages name" "version".
- "email" should allow to enter a valid email address to receive notifications are the same output as the URL (Notes "output list")
- "id for anonymous subscription" is actually not an input field but URL containing a UUID for the requested list of packages to subscribe for. If I open the URL I want to see a "output list" as described in Notes.

Once registered per email I want to get once per day an email about my CVE's if the information changes.
If I have only an URL with an "if for anonymous subscription" I want to get realtime informations whenever I open the page. The page should not be precomputed to safe resources and might be throttled to avoid denial of service if called to often.  

**Notes:** 
- a valid version of Gardenlinux is any version that we have a manifest list of packages contained
- "output list" contains for any package I subscribed for with "list of Gardenlinux packages" or contained in my "version of Gardenlinux" with their corresponding CVEs and the date of first occurrence. e.g.
   "bind9 CVE-2013-12234 240522"
- notification emails need to contain an "unsubscribe" button so we can stop to inform recipients permanently 
   
## #2 developer tests  
**As a** a developer using a Gardenlinux base layer (OS / Container) 
**I want** to know when I add a certain package so my selection what impact it has
**So that**  I can see current CVE's introduced by adding the package
### Acceptance Criteria  
- [ ]  I want to use the webpage of GLVD to test for a single package and its introduced CVE's
- [ ] The state of a package shows a current state and clearly differentiate between current and historical CVE so I have an impression how much exposure this package has.
### Additional Details  
**Description:**
This is probably the most simple call against the GLVD service and just provides for a single package state. 
 
## #3 gardener user / hyperscaler user
**As a**  Gardener user (or user of a bigger hyperscaler)
**I want** to subscribe for a certain fixed version 
**So that** I will get informed when this version updates or new CVE's occurring
### Acceptance Criteria  
- [ ] subscription for a version works over the default name like 1443.
- [ ] If a minor version (like 1443.1) is included I want to get informations about CVE's added to that version. (see user story #1)
- [ ] If no minor version is supported (and therefore no package lists!) I want to get information about updates to that version   
- [ ] I get a message when ever a new minor version or a new stable version is available.
### Additional Details  
**Description:**
The important point in this story is, we have a special information format for new versions. e.g. 1443 new hotfix version 1443.5. This information should show what CVE's are closes and should also have a list of open CVE's in older versions.
So updates will be send out either there is a new CVE in a version or a new version closes one or more CVE's. 

**Notes:** 
- as new version a new minor is considered e.g. 1443.5 but also historical versions like 1443.1 or 1443.2 etc must be listed since it was only subscribed for 1443
- also follow on major versions should be listed. e.g. 1312 has a new stable successor 1443. Not all minor versions of the successor must be mentioned but a list of CVE's closed (so if there is a new minor of the successor there will be also some information on the old version since there is a new list of closed CVE's)
- older version are fully ignored ... it is only the subscribed version or newer  
**Dependencies:**
- User Story #1

## #4 CLI  
**As a**  User of Gardenlinux
**I want** to have a simple CLI tool for API functions
**So that**  I can use the GLVD functions from command line without a web browser 
### Acceptance Criteria  
- [ ] single package test (User Story #2) is integrated in apt installations. e.g. I install packages X and add therefore (output of apt) the following CVE's
- [ ] base layer monitoring (User Story #1) can be used anonymously by getting a URL based on my installed package list and the output can be shown everytime I login via motd. e.g. following open CVE's are know (...)
   
### Additional Details  
**Description:**
It is just a command line wrapper towards the functionality GLVD is providing. No subscription via email is mandatory (but possible so it is easy to script) 

**Notes:** 
- based only on package lists since the version might be a valid entry point but since this will be command line based it will be very likely more modifications to the system are expected. No complicated convert back to the installed version should be implemented
-  
**Dependencies:**
- User Story #1
- User Story #2

## OCM  
**As a** OCM tool   
**I want** want to subscribe for CVE's of a certain Gardenlinux version
**So that**  I can update my security relevant information based on the version of this product
### Acceptance Criteria  
- [ ]  the OCM tool creates a list of open CVE's for a certain version (like in User Story #1) and uploads it in the expected format to related OCM documents
- [ ] the check is either done once a day (User Story #1) or every time a new Gardenlinux version is released (part of the release process)
### Additional Details  
**Description:**
Should be completely integrated in the release process (github) of Gardenlinux. And needs to contain the data expected by OCM.
**Notes:** 
- the process is completely automated and should not rely on email subscription
**Dependencies:**
- User Story #1

