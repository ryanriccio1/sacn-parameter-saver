import sys
import getopt
import sacn

DESTINATION_UNIVERSE = 5


def get_values():
    global DESTINATION_UNIVERSE
    number_pixels = 0
    combine_pixels = 0
    source_universe_start = 0
    source_address_start = 0
    source_universe_end = 0
    source_address_end = 0

    # Remove 1st argument from the
    # list of command line arguments
    argument_list = sys.argv[1:]

    # Options
    options = "hn:c:s:d:"

    # Long options
    long_options = ["help", "number_pixels=", "combine_pixels=", "source_address=", "destination_address="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argument_list, options, long_options)

        # checking each argument
        for current_argument, current_value in arguments:

            if current_argument in ("-h", "--help"):
                print("Displaying Help")

            elif current_argument in ("-n", "--number_pixels="):
                print(f"Number of Pixels:\t{current_value}")
                number_pixels = current_value

            elif current_argument in ("-c", "--combine_pixels="):
                print(f"Combine Pixels:\t{current_value}")
                combine_pixels = current_value

            elif current_argument in ("-s", "--source_address="):
                print(f"Source Address:\t{current_value}")
                source_start, source_end = current_value.split("-")
                source_universe_start, source_address_start = source_start.split(".")
                source_universe_end, source_address_end = source_end.split(".")

            elif current_argument in ("-d", "--destination_universe="):
                print(f"Dest Universe:\t{current_value}")
                DESTINATION_UNIVERSE = int(current_value)

        return int(number_pixels), int(combine_pixels), int(source_universe_start), \
               int(source_address_start), int(source_universe_end), int(source_address_end), \

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))


def main():
    number_pixels, combine_pixels, source_universe_start, \
    source_address_start, source_universe_end, source_address_end = get_values()

    receiver = sacn.sACNreceiver()
    receiver.start()  # start the receiving thread

    sender = sacn.sACNsender(source_name="Sexy AF SACN Source", bind_address="192.168.1.47")  # provide an IP-Address to bind to if you are using Windows and want to use multicast
    sender.start()  # start the sending thread

    max_pixels = int(512 / combine_pixels / 3)
    print(f"MAX PIXELS PER UNIVERSE:\t{max_pixels}")

    universe_range = source_universe_end - source_universe_start
    while universe_range >= 0:
        # define a callback function
        print(f"Listening on universe:\t\t{source_universe_start + universe_range}")
        print(f"Sending on universe:\t\t{DESTINATION_UNIVERSE}")
        sender.activate_output(DESTINATION_UNIVERSE)  # start sending out data in the 1st universe
        sender[DESTINATION_UNIVERSE].multicast = True  # set multicast to True

        @receiver.listen_on('universe', universe=source_universe_start + universe_range)
        def callback(packet):  # packet type: sacn.DataPacket
            temp_data = []
            for pixel in range(max_pixels):
                for iteration in range(combine_pixels):
                    temp_data.append(packet.dmxData[pixel + pixel * 2])
                    temp_data.append(packet.dmxData[pixel + pixel * 2 + 1])
                    temp_data.append(packet.dmxData[pixel + pixel * 2 + 2])

            sender[DESTINATION_UNIVERSE].dmx_data = temp_data
            print(packet.dmxData)  # print the received DMX data

        receiver.join_multicast(source_universe_start + universe_range)
        universe_range -= 1


if __name__ == "__main__":
    main()
