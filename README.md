# nac
Nagios Configuration utility

This Utility will allow you to quickly make changes to your nagios
configuration by role, and then imprint that confguration on nagios
servers according to a list of facts about the servers.

It allows servers to be autopopulated into nagios though puppet.

It is built for a large infrastructure with multiple silos each
needing to be monitored seperatly.

There is currently some majior work I need to do including fixing
the login.cgi, right now it has some test ldap junk in it, also 
creating an install script. 

I would like to move much of the ui side of this over from bash
to php or something better.
