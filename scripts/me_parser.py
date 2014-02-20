# -*- coding: utf-8 -*-

import argparse

from uefi_firmware.me import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description= "Parse an Intel ME container's partitions and code modules.")
    parser.add_argument('-e', "--extract", action="store_true", help="Extract all modules/partitions.")
    parser.add_argument("file", help="The file to work on")
    args = parser.parse_args()

    try:
        with open(args.file, 'rb') as fh: input_data = fh.read()
    except Exception, e:
        print "Error: Cannot read file (%s) (%s)." % (args.file, str(e))
        sys.exit(1)

    extract = False
    offset = 0
    f = input_data

    me_manifest = MeManifestHeader(input_data)
    me_manifest.process()

    me_manifest.showinfo()
    #me_manifest.show_structure()
    sys.exit(1)

    if input_data[offset:offset+8] == "\x04\x00\x00\x00\xA1\x00\x00\x00":
        while True:
            manif = get_struct(f, offset, MeManifestHeader)
            manif.parse_mods(f, offset)
            manif.pprint()
            if extract:
                manif.extract(f, offset)
            if manif.partition_end:
                offset += manif.partition_end
                print "Next partition: +%08X (%08X)" % (manif.partition_end, offset)
            else:
                break
            if f[offset:offset+8] != "\x04\x00\x00\x00\xA1\x00\x00\x00":
                break    

def old_main():
    print "Intel ME dumper/extractor v0.1"
    if len(sys.argv) < 2:
        print "Usage: dump_me.py MeImage.bin [-x] [offset]"
        print "   -x: extract ME partitions and code modules"
    else:
        fname = sys.argv[1]
        extract = False
        offset = 0
        for opt in sys.argv[2:]:
            if opt == "-x":
                extract = True
            else:
                offset = int(opt, 16)
        f = open(fname, "rb").read()
        off2 = parse_descr(f, offset, extract)
        if off2 != -1:
            offset = off2
            try:
               os.mkdir("ME Region")
            except:
               pass
            os.chdir("ME Region")
        if f[offset:offset+8] == "\x04\x00\x00\x00\xA1\x00\x00\x00":
            while True:
                manif = get_struct(f, offset, MeManifestHeader)
                manif.parse_mods(f, offset)
                manif.pprint()
                if extract:
                    manif.extract(f, offset)
                if manif.partition_end:
                    offset += manif.partition_end
                    print "Next partition: +%08X (%08X)" % (manif.partition_end, offset)
                else:
                    break
                if f[offset:offset+8] != "\x04\x00\x00\x00\xA1\x00\x00\x00":
                    break
        elif f[offset:offset+8] == "\x02\x00\x00\x00\xA1\x00\x00\x00":
            manif = get_struct(f, offset, AcManifestHeader)
            manif.pprint()
        else:
            fpt = MeFptTable(f, offset)
            fpt.pprint()
            if extract:
                fpt.extract(f, offset)
        if off2 != -1:
            os.chdir("..")