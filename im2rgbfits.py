# im2rgbfits CL0024.png -over -header det.fits
# WILL HONOR WCS FROM headerfile

# im2rgbfits.py
# ~/ACS/CL0024/color/production/color.py
# ALSO SEE pyfits.pdf (Pyfits manual)

#from coetools import *
from PIL import Image
#import pyfits
import astropy.io.fits as pyfits
import sys, os
import string
from os.path import exists, join
from numpy import *

#################################

def str2num(str, rf=0):
    """CONVERTS A STRING TO A NUMBER (INT OR FLOAT) IF POSSIBLE
    ALSO RETURNS FORMAT IF rf=1"""
    try:
        num = string.atoi(str)
        format = 'd'
    except:
        try:
            num = string.atof(str)
            format = 'f'
        except:
            if not string.strip(str):
                num = None
                format = ''
            else:
                words = string.split(str)
                if len(words) > 1:
                    num = map(str2num, tuple(words))
                    format = 'l'
                else:
                    num = str
                    format = 's'
    if rf:
        return (num, format)
    else:
        return num

def params_cl(converttonumbers=True):
    """RETURNS PARAMETERS FROM COMMAND LINE ('cl') AS DICTIONARY:
    KEYS ARE OPTIONS BEGINNING WITH '-'
    VALUES ARE WHATEVER FOLLOWS KEYS: EITHER NOTHING (''), A VALUE, OR A LIST OF VALUES
    ALL VALUES ARE CONVERTED TO INT / FLOAT WHEN APPROPRIATE"""
    list = sys.argv[:]
    i = 0
    dict = {}
    oldkey = ""
    key = ""
    list.append('')  # EXTRA ELEMENT SO WE COME BACK AND ASSIGN THE LAST VALUE
    while i < len(list):
        if striskey(list[i]) or not list[i]:  # (or LAST VALUE)
            if key:  # ASSIGN VALUES TO OLD KEY
                if value:
                    if len(value) == 1:  # LIST OF 1 ELEMENT
                        value = value[0]  # JUST ELEMENT
                dict[key] = value
            if list[i]:
                key = list[i][1:] # REMOVE LEADING '-'
                value = None
                dict[key] = value  # IN CASE THERE IS NO VALUE!
        else: # VALUE (OR HAVEN'T GOTTEN TO KEYS)
            if key: # (HAVE GOTTEN TO KEYS)
                if value:
                    if converttonumbers:
                        value.append(str2num(list[i]))
                    else:
                        value = value + ' ' + list[i]
                else:
                    if converttonumbers:
                        value = [str2num(list[i])]
                    else:
                        value = list[i]
        i += 1

    return dict

def striskey(str):
    """IS str AN OPTION LIKE -C or -ker
    (IT'S NOT IF IT'S -2 or -.9)"""
    iskey = 0
    if str:
        if str[0] == '-':
            iskey = 1
            if len(str) > 1:
                iskey = str[1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    return iskey

def strend(str, phr):
    return str[-len(phr):] == phr

def decapfile(name, ext=''):
    """REMOVE EXTENSION FROM FILENAME IF PRESENT
    IF ext LEFT BLANK, THEN ANY EXTENSION WILL BE REMOVED"""
    if ext:
        if ext[0] != '.':
            ext = '.' + ext
        n = len(ext)
        if name[-n:] == ext:
            name = name[:-n]
    else:
        if strend(name, '.gz'):
            name = name[-3:]
        i = name.rfind('.')
        if i > -1:
            name = name[:i]
    return name

def loadrgb(infile):
    im = Image.open(infile)
    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    # rgb = array(im.getdata())
    rgb = asarray(im)  # numpy
    print(rgb.shape)
    #nx, ny = im.size
    #rgb.shape = (ny,nx,3)
    rgb = transpose(rgb, (2,0,1))
    rgb = rgb[:3]  # in case there's an alpha channel on the end
    rgb.flags.writeable = False  # DEFAULT IS CAN'T EDIT IT!
    return rgb

#################################

def im2rgbfits(infile, rgbfile='', overwrite=False, headerfile=None, flip=False):
    if rgbfile == '':
        rgbfile = decapfile(infile) + '_RGB.fits'
        
    if exists(rgbfile):
        if overwrite:
            delfile(rgbfile)
        else:
            print(rgbfile, 'EXISTS')
            sys.exit(1)
    
    #im = Image.open(infile)
    #print('Loading data...')
    #data = array(im.getdata())
    #nxc, nyc = im.size
    #data.shape = (nyc,nxc,3)
    #data = transpose(data, (2,0,1))
    data = loadrgb(infile)
    
    #hdu = pyfits.PrimaryHDU()
    header = headerfile and pyfits.getheader(headerfile)
    hdu = pyfits.PrimaryHDU(None, header)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(rgbfile)

    try:  # If there's a 'SCI' extension, then that's where the WCS is
        header = pyfits.getheader(headerfile, 'SCI')
    except:
        pass
    
    if header != None:
        if 'EXTNAME' in header.keys():
            del(header['EXTNAME'])
    
    for i in range(3):
        print('RGB'[i])
        data1 = data[i]
        if flip:
            data1 = flipud(data1)
        pyfits.append(rgbfile, data1, header)
        
    print(rgbfile, 'NOW READY FOR "Open RGB Fits Image" in ds9')


if __name__ == '__main__':
    infile = sys.argv[1]
    
    outfile = ''
    if len(sys.argv) > 2:
        file2 = sys.argv[2]
        if file2[0] != '-':
            outfile = file2
    
    params = params_cl()
    overwrite = 'over' in params.keys()
    headerfile = params.get('header', None)
    
    im2rgbfits(infile, outfile, overwrite=overwrite, headerfile=headerfile)


#hdulist = pyfits.open(rgbfile)
#hdulist.info()
