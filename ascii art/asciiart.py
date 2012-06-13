# ASCII Art Maker
import PIL
import random
import asciibrowser
from bisect import bisect

# Choosing image
# Grayscale Tones
grayscale = [
            " ",
            " ",
            "-",
            ".`",
            "'",
            ":",
            "=",
            "+",
            "EC",
            "H$",
            "#",
            "&",
            "%"
            ]

# Use bisect class for luminosity values
zonebounds = [21,42,63,84,105,126,147,168,189,210,231,252]

# Open image and resize
# experiment with aspect ratio
# Code from Steven Kay

im = Image.open(r"images/liberty.jpg")
im = im.resize((150, 140), Image.BILINEAR)
im = im.convert("L") # convert to mono

# working with pixels, build up string
str = ""
for y in range(0,im.size[1]):
    for x in range(0,im.size[0]):
        lum = 255-im.getpixel((x,y))
        row = bisect(zonebounds, lum)
        possibles = grayscale[row]
        str = str + possibles[random.randint(0,len(possibles)-1)]
    str = str + "\n"

# saving to txt file
saveFile = open('ascii/liberty.txt', 'w')
saveFile.write(str)
saveFile.close()

print "Image has been converted to ascii"