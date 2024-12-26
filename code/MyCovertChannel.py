from CovertChannelBase import CovertChannelBase
from scapy.all import IP, TCP, sniff
import time
import random

class MyCovertChannel(CovertChannelBase):
    """
    Implementation of a covert channel using TCP RST flag manipulation.
    This channel encodes information by manipulating the RST flag in TCP packets,
    using two's complement encoding for added stealth and reliability.
    """
    
    def _init_(self):
        """Initialize the covert channel with base configuration."""
        super()._init_()

    def two_complement(self, binary_str):
        """
        Calculate two's complement of a 4-bit binary string.
        For example: "0101" -> "1011" (flip bits and add 1)
        """
        num = (int(binary_str, 2) + 1) & 0b1111
        result = ~num & 0b1111
        return format(result, '04b')

    def reverse_two_complement(self, binary_str):
        """
        Reverse the two's complement encoding to get original bits.
        For example: "1011" -> "0101"
        """
        num = ~(int(binary_str, 2)) & 0b1111
        result = (num - 1) & 0b1111
        return format(result, '04b')

    def create_encoded_packet(self, seq_num, bits):
        """
        Creates TCP packets for a 4-bit group with proper encoding.
        
        Args:
            seq_num (int): Base sequence number for this group
            bits (str): 4-bit binary string to encode
            
        Returns:
            list: List of 4 TCP packets with encoded flags
        """
        packets = []
        
        encoded_bits = self.two_complement(bits)
        
        for idx, bit in enumerate(encoded_bits):
            packet_seq = seq_num + idx
            
            packet = IP(src="172.18.0.2", dst="172.18.0.3")/TCP(
                sport=8000,
                dport=8000,
                seq=packet_seq
            )
            
            if int(bit):
                packet[TCP].flags = "R"  
            else:
                packet[TCP].flags = ""  
            
            packets.append(packet)
            
        return packets

    def send(self, log_file_name, base_seq, timing_variance):
        """
        Sends the complete binary message as encoded TCP packets.
        """
        binary_message = self.generate_random_binary_message_with_logging(log_file_name)     
        current_seq = base_seq
        message_length = len(binary_message)

        start_time = time.time()
        for i in range(0, len(binary_message), 4):
            four_bits = binary_message[i:i+4]
            
            packets = self.create_encoded_packet(current_seq, four_bits)
            for packet in packets:
                super().send(packet)
                self.sleep_random_time_ms(1, timing_variance)
            
            current_seq += 4

        end_time = time.time()
        

        transmission_time = end_time - start_time
        channel_capacity = 128/transmission_time
        
        # # Print results
        # print(f"Message length: {message_length} bits")
        # print(f"Transmission time: {transmission_time:.2f} seconds")
        # print(f"Channel capacity: {channel_capacity:.2f} bits per second")

    def receive(self, base_seq, timing_threshold, buffer_size, log_file_name):
        """
        Receives and decodes the covert channel message.
        """
        received_bits = []           
        current_group = [''] * 4     
        group_packets_received = 0   
        current_group_base = base_seq  
        message = ""                
        stop_found = False 
        
        def packet_callback(packet):
            """Process each received packet."""
            nonlocal received_bits, current_group, group_packets_received
            nonlocal current_group_base, message, stop_found
            
            if stop_found:
                return True
            
            if packet.haslayer(TCP) and packet[TCP].dport == 8000:
                seq = packet[TCP].seq
                offset = seq - current_group_base
                
                if 0 <= offset < 4 and current_group[offset] == '':
                    rst_flag = '1' if packet[TCP].flags & 0x04 else '0'
                    current_group[offset] = rst_flag
                    group_packets_received += 1

                    if group_packets_received == 4:
                        group_bits = ''.join(current_group)
                        decoded_bits = self.reverse_two_complement(group_bits)
                        received_bits.extend(decoded_bits)
                        
                        while len(received_bits) >= 8:
                            char_bits = ''.join(received_bits[:8])
                            received_bits = received_bits[8:]
                            char = self.convert_eight_bits_to_character(char_bits)
                            
                            message += char
                            if char == '.':
                                self.log_message(message, log_file_name)
                                stop_found = True
                                return True
                        
                        current_group = [''] * 4
                        group_packets_received = 0
                        current_group_base += 4
            
            return False
        
        sniff(prn=packet_callback,
              stop_filter=packet_callback,
              filter="tcp and port 8000",
              store=0)
        