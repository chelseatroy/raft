# To Run this Repo

1. You have to pre-populate the server logs with information about which other servers to contact about elections, or else they just send out broadcasts to no one and keep voting for themselves.
I just tried it on my end. Here is a step by step of how to start the cluster. 1. in raft/logs, make a file called tom_log.txt, jerry_log.txt, and spike_log.txt. In each of those files, paste the following and nothing else 0 0 set unreachable 1 0 register tom 10000 2 0 register jerry 10001 3 0 register spike 10002
This tells the servers who else they're supposed to be contacting.
2. Open three terminal windows. In each one, go to the raft directory. Then, in each of the tree, paste one of the following: python start_server.py tom 10000 python start_server.py jerry 10001 python start_server.py spike 10002
Now you need to wait 10-20 seconds for someone to get elected the leader.
3. Open a fourth terminal window and navigate to the raft directory. Type python start_client.py 10000
And when it says to type your message, type client|@get a
client = the sender pipe = delimiter for port (client does not have a port which is why there's nothing between pipe and @) @ = delimiter for message get a = "get the value at the key a" There is no value at the key a at the moment. This is fine.
The server will respond either with "name|port@" (if you guessed the port of the leader correctly) or "received b'name|port@I am not the leader. The last leader I heard from is some_other_server_name."
if it's the latter, shut down the client, and then restart the client pointing at the port of the server indicated in the last message as the leader.
Then when you send "client|@get a" you should get back from the server "name|port@"
That means you're talking to the leader. From there you can issue commands like "client|@set a 1"
When you send that, the server will probably close the connection on you because it is very rude. However, it will execute and replicate the command (you can verify this by checking the tom_log.txt, jerry_log.txt, and spike_log.txt files).
