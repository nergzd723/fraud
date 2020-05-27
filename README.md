# Sloth

#### UART over sound

##### Sloth aims for a UART interface over sound. 

Standard UART specification is designed for **stable** connection. As you probably might know, sound is not stable.

Sloth can encode data for sound transmission, and, you know **transmit** it!

Sloth uses big endian ~~because I hate little endian~~ because it's much easier to do in RIGHT order.

#### How does it work?

##### Format of stream

Most UART communicators use 8-N-1 format to transfer data. Sloth... is not.

Eventually Sloth will support kinda 8-N-1 format, but Sloth has variable speed.

Sloth marks each 8 bits by BYTE frequency.

*L- low, H - high*

Bits are encoded like normal: 010101010 will be encoded as LHLHLHLH.

But since we are desynchronised, we need STOP marks when same bytes collide: 01111010 becomes LHSHSHSHLHL

Start of transmission is declared with START frequency, end of transmission - with END frequency.

#### Speed

Sound is not good for signals. And for speed too. Max theoretical speed is 32 bits per second(capital latin U letters, 0.1 delay) but I had no luck reaching that speed.

My best was 9 bits per second(capital latin U letters, 0.35 delay), and 14 bits per second(good mic, no reflections, 0.23 delay)

#### Errors

###### Corrupted byte

It means that Sloth's byte has less than 8 bits. At this point it's unrecoverable, but maybe in the future we can search for any STOP signals to recreate byte. Again, it still won't work 100% all time, and be useful only for 10-15% of corrupted bytes.

###### No distinguisher

That means that Sloth hasn't found BYTE distinguisher between bytes. If nothing else is wrong, it will split bytes and continue parsing.

###### Irrecoverable distinguisher error

It means that:

- you lost more than one distinguisher in row;
- you got more bytes than expected;
- you got less bytes than expected, **including** distinquisher

You lose one or two bytes either way.

#### Standard frequencies

Standard frequencies are:

- HIGH 1400
- LOW 2100
- STOP 1000
- START 600-700
- BYTE 1800
- END 3600

Sloth accepts frequency if it approximately(100 Hz less or 100 Hz more) equal

High-frequency standard batch probably will be released too.



Have fun debugging!
