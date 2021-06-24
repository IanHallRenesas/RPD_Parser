import sys
import argparse
import xml.etree.ElementTree as ET

# First parameter on the command line should be the project's .rpd file which conatins the boundary sizes
# Second optional parameter should be the RFP project configuration .rpj file used with the '-r' switch
# 
# The boundary information will be written to the terminal
# The .rpj file will be updated with the boundary values and the boundary setting option will be set to True

def main():
    parser = argparse.ArgumentParser(description="Parse .rpd file and display secure/non-secure boundaries.\n Optionally write boundaries to RFP configuration file",
                                    epilog='e.g. Display just the boundaries:\n \
    \tpython rpd_parser.py <rpd file>\n\n \
    Optionally write to RFP .rpj project configuration file:\n \
    \tpython rpd_parser.py <rpd file> -r <rpj file>\n\n', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('rpd_file', type=str, help='RPD file to parse')
    parser.add_argument('-r', '--rpjfile', type=str, help='RFP .rpj file to write boundary information into.')
    args = parser.parse_args()
    
    # attempt to open the RPD file
    try:
        f = open(args.rpd_file, "r")
    except:
        print("Failed to open " + args.rpd_file)
        sys.exit()
    
    rpd_lines = f.readlines()
    f.close()

    code_flash_secure   = 0
    code_flash_nsc      = 0
    data_flash_secure   = 0
    sram_secure         = 0
    sram_nsc            = 0

    for line in rpd_lines:
        if ("RAM_S_SIZE=" in line):
            l = len("RAM_S_SIZE=") + 2
            sram_secure += int(line[l:], base=16)
        elif ("RAM_C_SIZE=" in line):
            l = len("RAM_C_SIZE=") + 2
            sram_nsc += int(line[l:], base=16)
        elif (line[:13] == "FLASH_S_SIZE="):
            l = len("FLASH_S_SIZE=") + 2
            code_flash_secure += int(line[l:], base=16)
        elif (line[:13] == "FLASH_C_SIZE="):
            l = len("FLASH_C_SIZE=") + 2
            code_flash_nsc += int(line[l:], base=16)
        elif ("DATA_FLASH_S_SIZE=" in line):
            l = len("DATA_FLASH_S_SIZE=") + 2
            data_flash_secure += int(line[l:], base=16)

    print("Code Flash Secure \t(kB) : ", str(int(code_flash_secure / 1024)))
    print("Code Flash NSC \t\t(kB) : ", str(int(code_flash_nsc / 1024)))
    print("Data Flash Secure \t(kB) : ", str(int(data_flash_secure / 1024)))
    print("SRAM Secure \t\t(kB) : ", str(int(sram_secure / 1024)))
    print("SRAM NSC \t\t(kB) : ", str(int(sram_nsc / 1024)))

    if (args.rpjfile):
        # Write the values into the RFP configuration file
    
        try:
            tree = ET.parse(args.rpjfile)
        except:
            print("ERROR: Couldn't open the RFP configuration file")
            sys.exit()

        root = tree.getroot()

        setboundary = root.find("./DeviceOptionTab/SetBoundary")
        setboundary.text = "True"
        boundarycfs = root.find("./DeviceOptionTab/BoundaryCFS")
        boundarycfs.text = str(int(code_flash_secure / 1024))
        boundarycfnsc = root.find("./DeviceOptionTab/BoundaryCFNSC")
        boundarycfnsc.text = str(int(code_flash_nsc / 1024))
        boundarydfs = root.find("./DeviceOptionTab/BoundaryDFS")
        boundarydfs.text = str(int(data_flash_secure / 1024))
        boundarysrs = root.find("./DeviceOptionTab/BoundarySRS")
        boundarysrs.text = str(int(sram_secure / 1024))
        boundarysrnsc = root.find("./DeviceOptionTab/BoundarySRNSC")
        boundarysrnsc.text = str(int(sram_nsc / 1024))

        # write out the modified file
        tree.write(args.rpjfile)

        print("\n" + args.rpjfile + " updated.")

if __name__ == "__main__":
    main()
