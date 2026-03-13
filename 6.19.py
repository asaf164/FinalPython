"""
Author: Asaf Biran
program name - 6.19
The program scans ports 20 to 1024 on a target computer by sending SYN packets
and printing the ones that reply with a SYN-ACK
"""


from scapy.all import IP, TCP, sr1
import logging

#logging setup
logging.basicConfig(filename='scan_results.log', level=logging.INFO, format='%(message)s')

target_ip = input("Please enter the target IP: ")

print("Scanning ports 20 to 1024")
logging.info("Starting scan for IP: " + target_ip)

#loop for all ports
for port in range(20, 1025):
    #builds the syn packet
    syn_packet = IP(dst=target_ip) / TCP(dport=port, flags="S")

    #sends the packet and waits 0.5 seconds for an answer
    response = sr1(syn_packet, timeout=0.5, verbose=False)
    #checks for answers
    if response != None:

        #checks if the answer is syn ack
        if response.haslayer(TCP) and response[TCP].flags == "SA":
            result_message = "Port " + str(port) + " is OPEN"
            print(result_message)  #print to the screen
            logging.info(result_message)  #saves to the logs file

print("Scan finished")
logging.info("Scan finished!")