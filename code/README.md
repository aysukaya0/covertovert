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
