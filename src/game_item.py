import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import re
import urlparse

def comparePlatforms(platform1, platform2):
    """
    This utility function canonicalizes platforms and tests them for equality.
    """
    platform1 = re.sub("[^a-z0-9 ]", "", platform1.lower())
    platform2 = re.sub("[^a-z0-9 ]", "", platform2.lower())
    if platform1 == platform2:
        return True

    # Don't want "nintendo entertainment system" to match "super nintendo entertainment system"
    SNES = re.compile("((^|[^a-z])snes([^a-z]|$)|super nintendo)")
    if SNES.match(platform1) or SNES.match(platform2):
        return SNES.match(platform1) and SNES.match(platform2)

    NES = re.compile("((^|[^a-z])nes([^a-z]|$)|nintendo entertainment system)")
    if NES.match(platform1):
        return NES.match(platform2)
    elif NES.match(platform2):
        return NES.match(platform1)

    for company in ["microsoft", "nintendo", "sega", "sinclair", "sony"]:
        if platform1.startswith(company):
            platform1 = platform1[len(company):].strip()
        if platform2.startswith(company):
            platform2 = platform2[len(company):].strip()

    aliases = {
        "atari xe": "atari 8bit",
        "c64":      "commodore 64",
        "osx":      "max os",
        "n64":      "64", # nintendo was stripped
        "nds":      "ds",
        "ndsi":     "dsi",
        "gb":       "game boy",
        "gba":      "game boy advance",
        "gbc":      "game boy color",
        "gcn":      "gamecube",
        "ngc":      "gamecube",
        "gg":       "game gear",
        "sms":      "master system",
        "ps":       "playstation",
        "ps2":      "playstation 2",
        "ps3":      "playstation 3",
        "ps4":      "playstation 4",
        "vita":     "playstation vita",
        "psp":      "playstation portable",
        "ws":       "wonderswan",
        "wsc":      "wonderswan color",
    }
    platform1 = aliases.get(platform1, platform1)
    platform2 = aliases.get(platform2, platform2)

    # Finally, compare without spaces so that "game boy" matches "gameboy"
    return platform1.replace(" ", "") == platform2.replace(" ", "")


class ResolvePlatform(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier),
        demands.requiredClass("item"),
    ]

    supply = [
        supplies.ugpradeClass("item.game"), # NOT IMPLEMENTED YET
        supplies.emit(edamontology.data_3106), # Platform
    ]

    def run(self):
        path = urlparse.urlparse(self.subject[dc.identifier]).path
        ext = path[path.rindex(".") + 1 : ].lower() if "." in path else ""

        # Sources:
        # http://www.file-extensions.org/filetype/extension/name/emulator-files
        # http://justsolve.archiveteam.org/wiki/ROM_and_memory_images
        ext_to_platform = {
            "32x":    "Sega Genesis",      # Sega GENESIS ROM image file
            "64b":    "Commodore 64",      # Commodore C64 emulator file
            "64c":    "Commodore 64",      # Commodore C64 emulator file
            "a26":    "Atari 2600",        # Atari 2600 ROM image file
            "a52":    "Atari 5200",        # Atari 5200 ROM image file
            "a78":    "Atari 7800",        # Atari 5200 ROM image file
            "agb":    "Game Boy Advance",  # Nintendo Game Boy Advance ROM image
            "adf":    "Amiga",             # Amiga disk file
            "atr":    "Atari 8-bit",       # Atari 8-bit disk image
            "boxer":  "Mac",               # Boxer for Mac game archive file
            "bsx":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "c64":    "Commodore 64",      # Commodore 64 ROM image
            "cgb":    "Game Boy Color",    # Nintendo GameBoy Color emulator ROM image file
            "chd":    "Arcade",            # MAME compressed hard disk file
            "dhf":    "Amiga",             # AMIGA emulator disk image ROM file
            "dol":    "GameCube",          # Nintendo GameCube (codename "Dolphin" executable)
            "dx2":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "fam":    "NES",               # Nintendo Entertainment System Famicom emulator ROM image
            "fdi":    "Amiga",             # Amiga disk file
            "fds":    "NES",               # Nintendo Famicom (NES) disk system file
            "fig":    "Super Nintendo",    # Super Nintendo game-console ROM image
            "g64":    "Commodore 64",      # C64 emulator disk image file
            "gb":     "Game Boy",          # Nintendo Gameboy ROM image
            "gba":    "Game Boy Advance",  # Nintendo Game Boy Advance ROM image
            "gbc":    "Game Boy Color",    # Nintendo GameBoy Color emulator ROM image file
            "gcz":    "GameCube",          # Dolphin emulator archive
            "gcn":    "GameCube",
            "gd3":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "gd7":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "gen":    "Sega Genesis",
            "gg":     "GameGear",
            "ggs":    "Game Boy",          # Gameboy emulator file
            "hdf":    "ZX Spectrum",       # ZX Spectrum IDE hard drive image file
            "hdz":    "Amiga",             # Amiga hard disk image file
            "jma":    "Super Nintendo",    # Snes9x emulator ROM image
            "lnx":    "Atari Lynx",        # Atari Lynx ROM image file
            "mgt":    "ZX Spectrum",       # ZX Spectrum emulator disk image
            "md":     "Sega Genesis",
            "n64":    "Nintendo 64",       # Nintendo 64 Emulation ROM image file (wordswapped)
            "nd5":    "Nintendo DS",       # Nintendo DS game ROM file
            "nds":    "Nintendo DS",       # Nintendo DS game ROM image file
            "nes":    "NES",               # Nintendo Entertainment System ROM image
            "nez":    "NES",               # NES ROM emulator image file
            "ngc":    "Neo Geo",           # Neo Geo Pocket ROM image file
            "ngp":    "Neo Geo",
            "npc":    "Neo Geo",
            "pce":    "TurboGrafx 16",     # Mednafen PC Engine file
            "pro":    "Atari 8-bit",       # APE Atari disk image file
            "sc":     "Sega SC-3000",      # Sega SC-3000 image file
            "sf7":    "Sega SF-7000",      # Sega SF-7000 ROM file
            "sfc":    "Super Nintendo",    # Nintendo SNES9x ROM file
            "sg":     "Sega SG-1000",
            "sgb":    "Super Game Boy",    # Super Gameboy image file
            "smc":    "Super Nintendo",    # Super Nintendo game-console ROM image
            "smd":    "Sega Genesis",      # Sega Genesis ROM emulator file
            "sms":    "Sega Master System",# Sega Master System ROM emulator file
            "st":     "Atari ST",          # Atari disk image file
            "swc":    "Super Nintendo",    # Snes9x-Next emulator ROM image
            "trd":    "ZX Spectrum",       # TR-DOS ZX Spectrum floppy disk image
            "ttp":    "Atari Falcon",      # Atari Falcon application
            "u00":    "Commodore 64",      # Commodore C64 universal file
            "unif":   "NES",               # FCEU-Next emulator ROM image
            "v64":    "Nintendo 64",       # Nintento 64 emulation ROM image file (byteswapped)
            "vb":     "Virtual Boy",       # Virtual Boy image file
            "wdf":    "Wii",               # Wiimm Nintendo Wii disc file
            "whd":    "Amiga",             # WinUAEX Amiga game ROM file
            "ws":     "WonderSwan",
            "wsc":    "WonderSwan Color",
            "x64":    "Commodore 64",      # Commodore 64 emulator disk image
            "z64":    "Nintendo 64",       # Nintento 64 emulation ROM image file (native)
        }

        platform = ext_to_platform.get(ext)
        if platform:
            self.subject.extendClass("item.game")
            self.subject.emit(edamontology.data_3106, platform)

module = [ ResolvePlatform ]
