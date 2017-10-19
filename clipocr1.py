
"""

  clipocr1.py

  Demonstrates a technique that often improves ocr quality on screen captures.

  Reads an image from the system clipboard,
  and writes to stdout various versions of the text recognized in the image.
  Uses tesseract OCR.
  
  The technique is based on judicious rescaling of image dimensions.
  
  SIDE EFFECT: 

    Creates image files and text file in current working directory.


  REQUIREMENTS:

    Written and tested 2014 March, 2014 April
    on an Ubuntu 12.04 system (64-bit Intel)

    Relies on system having these python packages installed
    (it's ok to install them as Ubuntu/Debian packages):

    - wx 
        for portable clipboard access.
    - PIL [can we make do with Pillow?]
        for rescaling the image
          NOTE: We might be able to get away with rewriting to use 
                  the right version(s) of wx for this instead?

    Relies on system having this software installed,
     e.g. as an Ubuntu/Debian package:

    - tesseract 
        the OCR software.

  Conveniently, these packages are all open source.


COPYRIGHT:

Copyright (c) 2014 Chris Niswander.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
from PIL import Image 
import wx      # just to access the system clipboard.


def get_file_text(fname):
  """Reads the text out of the text file having pathname /fname/."""
  with open(fname) as fin:
    return fin.read()
 
def read_test1(fname):
  """Demonstrates OCRing the text from an image file named /fname/, 
     and printing it to stdout.
     Makes multiple OCR attempts, 
     based on resizing the image to different size image files, 
     and prints multiple OCR attempts' text.
  """

  def params_textname(params):
     """Given /params/, a resize method specification from resize_methods,
        constructs a text string that can be used in a filename 
        for a resized/rescaled image.
     """
     params = params[0][0], params[0][1], params[1]
     return '_'.join([str(x).strip() for x in params])

  # do ocr on original, non-rescaled image.
  print 'ORIGINAL IMAGE:'
  print do_ocr_to_imagefile(fname)

  im1 = Image.open(fname)

  # List of image resizing methods to try.
  # Each method consists of:
  #   [Rescale factor tuple, image rescaling method].
  # A rescale factor tuple is (width-rescale-factor, height-rescale-factor)
  # Image rescaling method is given as eval()-able text because:
  #   - convenient for naming image files produced using that method.
  resize_methods = [
      [(2, 2), 'Image.BICUBIC'], 
      [(2, 2), 'Image.BILINEAR'],
      [(3, 2), 'Image.BICUBIC'],
      [(3, 2), 'Image.BILINEAR'],
      [(3, 3), 'Image.BICUBIC'],
      [(3, 3), 'Image.BILINEAR'],
    ]

  for resize_method in resize_methods:
    rescale = resize_method[0]
    im_resized = im1.resize(
       (im1.size[0] * rescale[0], im1.size[1] * rescale[1]),
       (eval (resize_method[1]) ))
    resized_path = fname + '__' + params_textname(resize_method) + '.png'
    print resized_path
    im_resized.save(resized_path)
    print do_ocr_to_imagefile(resized_path)

def do_ocr_to_imagefile(fname):
  """Runs tesseract command line utility on image file /fname/
     and returns the perceived text.

     SIDE EFFECTS:
       Creates file 3.txt in current working directory.
  """   
  os.system('tesseract ' + fname + ' 3' )  
    # ^ OCR text from the file named /resized_path/, save the text to 3.txt.
  return get_file_text('3.txt')    


def save_clipboard(fname):
  """Saves an image from the system clipboard to the filename /fname/."""
  app = wx.App()   
  if not wx.TheClipboard:
    del app
    raise Exception("can't get clipboard")
  wx.TheClipboard.Open()
  data = wx.BitmapDataObject()
  clipboard_getdata_status = wx.TheClipboard.GetData(data)
  wx.TheClipboard.Close()
  if not clipboard_getdata_status:
    del app
    raise Exception("couldn't find image data in clipboard")

  image = data.GetBitmap().ConvertToImage()
  image.SaveFile(fname, 1)  # 1 --> save as Windows bitmap.
  del app

def clippy():
  """Demonstrates OCRing the text from an image in the system clipboard, 
     and printing it to stdout.
     Makes multiple OCR attempts, 
     based on resizing the image to different sizes, 
     and prints multiple OCR attempts' text.
  """
  clippy_fname = 'image_from_clipboard'
  save_clipboard(clippy_fname)
  read_test1(clippy_fname)

clippy()

#---------------------------------------------------------------------------
# Test code not normally called, but tester might run it from e.g. IDE.
def clear_clipboard():
  """Clear the clipboard, which can be useful for error testing."""
  app = wx.App()   
  if not wx.TheClipboard:
    del app
    raise Exception("can't get clipboard")
  wx.TheClipboard.Open()
  wx.TheClipboard.Clear()
  wx.TheClipboard.Close()
  del app

