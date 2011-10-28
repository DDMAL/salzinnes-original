import os
import sys
import math
from vipsCC import VImage
from operator import itemgetter

class DivaServe(object):
    def __init__(self, directory, t=256, mode="memory"):
        """ <directory> is the directory of images to serve 
            "mode" can be either "memory" or "disk" for the cache mode to use
            if "mode" is "disk," you must also set "cachedir".
            <t> is be the tilesize. Default 256
        """

        self.imgdir = directory
        self.images = {}
        self.data = {}
        self.lowest_max_zoom = 0

        self.til_wid = t
        self.til_hei = t

        lmz = 0
        # Read image sizes on startup
        print >> sys.stderr, "loading images..."
        for i,f in enumerate(os.listdir(self.imgdir)):
            if os.path.splitext(f)[1] not in (".tif", ".tiff"):
                continue
            img = VImage.VImage(os.path.join(self.imgdir, f))
            img_wid = img.Xsize()
            img_hei = img.Ysize()
            del img

            max_zoom = self._get_max_zoom_level(img_wid, img_hei, self.til_wid, self.til_hei)
            if max_zoom > lmz:
                lmz = max_zoom
 
            self.images[i] = {
                'mx_w': img_wid,
                'mx_h': img_hei,
                'mx_z': max_zoom,
                'fn': os.path.join(self.imgdir, f)
            }

        self.lowest_max_zoom = lmz
        print >> sys.stderr, "images loaded"


    def get(self, zoom):
        if zoom in self.data.keys() and len(self.data[zoom]) > 0:
            return self.data[zoom]

        if zoom > self.lowest_max_zoom:
            zoom = 0
        elif zoom < 0:
            zoom = 0

        mx_h = mx_w = t_wid = t_hei = num_pages = max_ratio = 0
        pgs = []

        for v in self.images.itervalues():
            h = self._incorporate_zoom(v['mx_h'], self.lowest_max_zoom - zoom)
            w = self._incorporate_zoom(v['mx_w'], self.lowest_max_zoom - zoom)

            c = math.ceil(w / float(self.til_wid))
            r = math.ceil(h / float(self.til_hei))
            m_z = v['mx_z']
            fn = v['fn']
            
            pgs.append({
                'c': c,
                'r': r,
                'h': h,
                'w': w,
                'm_z': m_z,
                'fn': fn
            })

            if h > mx_h:
                mx_h = h

            if w > mx_w:
                mx_w = w
            
            ratio = h / float(w)
            max_ratio = ratio if ratio > max_ratio else max_ratio
            t_wid += w
            t_hei += h
            num_pages += 1
        pgs.sort(key=itemgetter("fn"))

        if num_pages > 0:
            a_wid = t_wid / float(num_pages)
            a_hei = t_hei / float(num_pages)

            dims = {
                'a_wid': a_wid,
                'a_hei': a_hei,
                'max_w': mx_w,
                'max_h': mx_h,
                'max_ratio': max_ratio,
                't_hei': t_hei,
                't_wid': t_wid
            }

            title = os.path.basename(self.imgdir).replace('-', ' ').title()

            self.data[zoom] = {
                'item_title': title,
                'dims': dims,
                'max_zoom': self.lowest_max_zoom,
                'pgs': pgs
            }
        else:
            self.data[zoom] = {}

        return self.data[zoom]

    def _get_max_zoom_level(self, iwid, ihei, twid, thei):
        largest_dim = max(iwid, ihei)
        t_dim = twid if iwid > ihei else thei

        zoom_levels = math.ceil(math.log((largest_dim + 1) / float(t_dim) + 1, 2))
        return int(zoom_levels)

    def _incorporate_zoom(self, img_dim, zoom_diff):
        return img_dim / float(2**zoom_diff)

class DivaException(BaseException):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
