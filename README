Testing tools
=============

speed_server.js
---------------

The speed_server is a server written in node.js. It is running on two places. One is located in a high bandwith datacenter, another on a low bandwith dsl landline. The speed_server collects bunches of udp packages, calculates the payload bandwith and stores the results in a log file.

speed_client.py
---------------

The speed_client is written in python. It uses scapy to generate bunches of udp packages. It has a rudimentary curses gui. You can choose, which server you will use (low bandwith, high bandwith) and flood them with udp packages. The speed client runs on Linux and has to be run as root.

Infos
=====

* one complete test-run consumed arround 40MB of traffic. Remember this, if you have volume paid internet access
* it would be great to have as much different(!) umts / 3g runs as possible
* it is not useful to perform more than one test-run per server (high / low bandwith) a time
* pay attention not to run other data connection while the test is running

Run tests
=========

Please run some test. Use Linux, if possible use umts / 3g. For Debian / Ubuntu you have to:

* install git (aptitude install git)
* install scapy (aptitude install python-scapy)
* checkout files (git clone git://github.com/Terminal21/payload_speed.git)
* change directory (cd payload_speed)
* become root (su / sudo -s)
* run the client (python speed_client.py)
* press 'h' or 'L' to chose a server
* press 's' to run a test loop

