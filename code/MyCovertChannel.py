from CovertChannelBase import CovertChannelBase
from scapy.all import IP, TCP, sniff
import time
import random

class MyCovertChannel(CovertChannelBase):
    def _init_(self):
        super()._init_()

    def two_complement(self, binary_str, bit_mask, base, bit_format,inc):
        num = (int(binary_str, base) + inc) & bit_mask
        result = ~num & bit_mask
        return format(result, bit_format)

    def reverse_two_complement(self, binary_str, bit_mask, base, bit_format,inc_dec):
        num = ~(int(binary_str, base)) & bit_mask
        result = (num - inc_dec) & bit_mask
        return format(result, bit_format)

    def create_encoded_packet(self, seq_num, bits, src_ip, dst_ip, src_port, dst_port, 
                            rst_flag, empty_flag, bit_mask, base, bit_format,inc):
        packets = []
        encoded_bits = self.two_complement(bits, bit_mask, base, bit_format,inc)
        
        for idx, bit in enumerate(encoded_bits):
            packet_seq = seq_num + idx
            packet = IP(src=src_ip, dst=dst_ip)/TCP(
                sport=src_port,
                dport=dst_port,
                seq=packet_seq
            )
            
            if int(bit):
                packet[TCP].flags = rst_flag
            else:
                packet[TCP].flags = empty_flag
            
            packets.append(packet)
            
        return packets

    def send(self, log_file_name, base_seq, timing_variance, src_ip, dst_ip, src_port, 
             dst_port, rst_flag, empty_flag, bit_group_size, bit_mask, base, min_delay,
             bit_format,inc):
        binary_message = self.generate_random_binary_message_with_logging(log_file_name)     
        current_seq = base_seq
        message_length = len(binary_message)

        start_time = time.time()
        for i in range(0, len(binary_message), bit_group_size):
            bit_group = binary_message[i:i+bit_group_size]
            
            packets = self.create_encoded_packet(current_seq, bit_group, src_ip, dst_ip, 
                                              src_port, dst_port, rst_flag, empty_flag, 
                                              bit_mask, base, bit_format,inc)
            for packet in packets:
                super().send(packet)
                self.sleep_random_time_ms(min_delay, timing_variance)
            
            current_seq += bit_group_size

        end_time = time.time()
        transmission_time = end_time - start_time
        channel_capacity = message_length/transmission_time

    def receive(self, base_seq, timing_threshold, buffer_size, log_file_name, dst_port, 
                bit_group_size, bit_mask, base, char_size, rst_mask, stop_char,
                empty_str, bit_format, initial_stop, initial_message, initial_bits,
                filter_template, store_val,init_group_packets,rst_reset,rst_set,inc_dec):
        received_bits = initial_bits.copy()           
        current_group = [empty_str] * bit_group_size     
        group_packets_received = init_group_packets   
        current_group_base = base_seq  
        message = initial_message                
        stop_found = initial_stop 
        
        def packet_callback(packet):
            nonlocal received_bits, current_group, group_packets_received
            nonlocal current_group_base, message, stop_found
            
            if stop_found:
                return True
            
            if packet.haslayer(TCP) and packet[TCP].dport == dst_port:
                seq = packet[TCP].seq
                offset = seq - current_group_base
                
                if 0 <= offset < bit_group_size and current_group[offset] == empty_str:
                    rst_flag = rst_set if packet[TCP].flags & rst_mask else rst_reset
                    current_group[offset] = rst_flag
                    group_packets_received += inc_dec

                    if group_packets_received == bit_group_size:
                        group_bits = empty_str.join(current_group)
                        decoded_bits = self.reverse_two_complement(group_bits, bit_mask, base, bit_format,inc_dec)
                        received_bits.extend(decoded_bits)
                        
                        while len(received_bits) >= char_size:
                            char_bits = empty_str.join(received_bits[:char_size])
                            received_bits = received_bits[char_size:]
                            char = self.convert_eight_bits_to_character(char_bits)
                            
                            message += char
                            if char == stop_char:
                                self.log_message(message, log_file_name)
                                stop_found = True
                                return True
                        
                        current_group = [empty_str] * bit_group_size
                        group_packets_received = init_group_packets
                        current_group_base += bit_group_size
            
            return False
        
        filter_str = filter_template.format(port=dst_port)
        sniff(prn=packet_callback,
              stop_filter=packet_callback,
              filter=filter_str,
              store=store_val)