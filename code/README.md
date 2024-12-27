# Covert Channel Using TCP RST Flag Manipulation

## Overview

This project implements a covert channel using TCP RST flag manipulation. The covert channel encodes and transmits information through the manipulation of TCP RST flags in network packets. This technique is designed to maximize stealth and efficiency while ensuring the reliability of the transmitted data.

## Key Features
- Encodes 4-bit binary data using two's complement for additional security.
- Sends and receives data through TCP packets with precise timing control.
- Decodes the transmitted message and verifies its integrity.
- Measures covert channel capacity in terms of bits per second.

## Implementation Details

### Encoding Mechanism
The 4-bit binary data is encoded using two's complement:
- **Two's Complement Encoding:** Flips the bits of the input binary string and adds 1.
- **Reverse Two's Complement:** Reverses the two's complement operation to retrieve the original data.

### Packet Transmission
- Each 4-bit group is transmitted using four TCP packets.
- The presence or absence of the RST flag in a packet encodes a single bit:
  - `1` for RST set.
  - `0` for RST unset.
- Sequence numbers are used to ensure proper ordering and identification of packets.

### Packet Reception
- Incoming packets are matched to their respective 4-bit groups using sequence numbers.
- Groups are decoded upon receiving all four packets.
- The final message is reconstructed character by character from the decoded binary data.
- The transmission stops upon detecting a period (`.`) in the message.

## Example Results
- **Message Length:** 128 bits  
- **Transmission Time:** 5.77 seconds  
- **Channel Capacity:** 22.20 bits per second

## Limitations of Parameters

In the covert channel implementation using TCP RST flag manipulation, certain parameters are designed with specific limitations based on the encoding and decoding logic, network conditions, and the nature of TCP/IP communication. Below are some of the key limitations and their rationale:

### 1. `bit_group_size (4)`
- **Limitation:** Set to 4 due to the encoding logic, which processes 4-bit groups.
- **Reason:** Two's complement encoding works on 4-bit groups. Altering the group size could disrupt the encoding/decoding process, potentially leading to incorrect data transmission.

### 2. `bit_mask (15)`
- **Limitation:** Set to 15 (binary `1111`), limiting the binary data to 4 bits.
- **Reason:** Ensures that only 4-bit values are processed, in line with the `bit_group_size`. A different bit mask could result in mismatched data during encoding or decoding.

### 3. `Base (2)`
- **Limitation:** Set to 2, representing binary data.
- **Reason:** The two's complement operation requires binary numbers. Using a different base would complicate the encoding and decoding processes.

### 4. `bit_format ("04b")`
- **Limitation:** The format is `"04b"`, ensuring that binary data is represented as 4-bit strings with leading zeros when necessary.
- **Reason:** This consistent representation is vital for matching the sequence number and proper data grouping in TCP packets.

### 5. `rst_mask (4)`
- **Limitation:** Set to 4, meaning only the RST flag is considered for encoding.
- **Reason:** The RST flag is used to encode data, and the `rst_mask` ensures no interference from other TCP flags.

### 6. `timing_threshold (100)`
- **Limitation:** Set to 100 milliseconds, defining the threshold for packet grouping.
- **Reason:** The timing threshold controls packet synchronization. Any changes might cause delays or missed packets, impacting the decoding process.

### 7. `buffer_size (1024)`
- **Limitation:** Set to 1024 bytes for the buffer size.
- **Reason:** Ensures enough space to store multiple TCP packets. Reducing it could result in packet loss, while increasing it unnecessarily consumes memory.

### 8. `char_size (8)`
- **Limitation:** Set to 8, corresponding to the size of a character in ASCII encoding.
- **Reason:** The system relies on 8-bit characters, and modifying this could lead to misinterpretation of binary data.

### 9. `stop_char (".")`
- **Limitation:** Set to `"."`, signaling the end of the message.
- **Reason:** Any change to this stop character requires synchronization between sender and receiver. A mismatch could prevent correct message termination.

## General Considerations
- **Sequence Numbering:** Proper management of sequence numbers is essential to ensure the correct order of packets. Mismanagement can result in incorrect decoding.
- **TCP/IP Network Conditions:** Performance depends on network reliability. Delays, packet loss, or retransmissions can impact covert channel performance and may necessitate adjustments in timing and buffer management.
- **Covert Channel Bandwidth:** The bandwidth is limited by the packet transmission rate, network speed, and timing thresholds. This must be accounted for when designing the covert channel.

