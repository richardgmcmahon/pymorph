import scipy.signal
import pyfits
import numpy as np
from numpy import fft
import os
import convolve as conv
def Convolve(image, kernal, zeropad=True):
    """ Convolution using numpy fft2. zeropad=True always in this function"""
    kernal = np.asarray(kernal)
    kernal = kernal.astype(np.float32) 
    kernal = kernal / kernal.sum() # Normalizing the kernal
    # The shape of the input including zero pading
    s0 = image.shape[0] + kernal.shape[0] - 1
    s1 = image.shape[1] + kernal.shape[1] - 1
    # The extra size
    es0 = (kernal.shape[0] - 1) / 2. 
    es1 = (kernal.shape[1] - 1) / 2.
    # The product of fourier transform of image and kernal. [s0, s1] is the 
    # dimension of the image with zero pading
    FouTra = np.multiply(fft.fft2(image, [s0, s1]), fft.fft2(kernal,[s0, s1]))
    # The inverse fourier transform of the products of trasforms gives the
    # convolved image
    ConvIm = fft.ifft2(FouTra).real
    # Removing the zero padded region
    ymin = np.floor(es0)
    ymax = np.floor(s0 - es0)
    xmin = np.floor(es1)
    xmax = np.floor(s1 - es1)
    ConvIm = ConvIm[ymin:ymax, xmin:xmax]
    return ConvIm

os.system('rm -f res.fits conv.fits conv1.fits')

f = pyfits.open('n5585_lR.fits')
z = f[0].data
f.close()
z = z.astype(np.float32)

f = pyfits.open('psf_1216482-1158151.fits')
ker = f[0].data
f.close()

ker = np.array([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])
ker = ker.astype(np.float32)

#zc = scipy.signal.fftconvolve(z, ker)
zc1 = scipy.signal.convolve2d(z, ker / ker.sum(), mode='same')
hdu = pyfits.PrimaryHDU(zc1)
hdu.writeto('conv1.fits')

zc = Convolve(z, ker) 
hdu = pyfits.PrimaryHDU(zc)
hdu.writeto('conv.fits')
#zc = conv.boxcar(z, (2,2))

#res = np.around(zc1) - np.around(zc)
res = zc1 - zc
hdu = pyfits.PrimaryHDU(res)
hdu.writeto('res.fits')
# The following implies that convolve2d in scipy and this function agrees well
print res[res > 1e-3].shape
