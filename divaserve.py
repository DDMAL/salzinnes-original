import os
import math
from vipsCC import VImage

import pdb

class DivaServe(object):
    def __init__(self, directory, **kwargs):
        """ <directory> is the directory of images to serve 
            "mode" can be either "memory" or "disk" for the cache mode to use
            if "mode" is "disk," you must also set "cachedir".

        """
        self.imgdir = directory
        self.images = {}
        self.data = {}

    def get(self, zoom, t=None):
        """ <t> should be the tilesize. Default 256 """
        if t:
            til_wid = t
            til_hei = t
        else:
            til_wid = 256
            til_hei = 256
        
        lowest_max_zoom = 0;
        pgs = []

        if zoom in self.data.keys():
            return self.data[zoom]

        if not self.images.keys():
            i = 0
            for dp, dn, fns in os.walk(self.imgdir):
                for f in fns:
                    if f.startswith("."):
                        continue
                    if os.path.splitext(f)[-1] != '.tif':
                        continue
                    img = VImage.VImage(os.path.join(dp, f))
                    img_wid = img.Xsize()
                    img_hei = img.Ysize()
                    del img

                    max_zoom = self._get_max_zoom_level(img_wid, img_hei, til_wid, til_hei)
                    if max_zoom > lowest_max_zoom:
                        lowest_max_zoom = max_zoom
                    
                    self.images[i] = {
                        'mx_w': img_wid,
                        'mx_h': img_hei,
                        'mx_z': max_zoom,
                        'fn': f
                    }

                    print "{0}: stats: {1}".format(f, self.images[i])

                    self.images['lmx'] = lowest_max_zoom
                    i += 1
        else:
            lowest_max_zoom = self.images['lmx']

        if zoom > lowest_max_zoom:
            zoom = 0
        elif zoom < 0:
            zoom = 0

        mx_h = mx_w = t_wid = t_hei = num_pages = max_ratio = 0

        for k,v in self.images.iteritems():
            if k == 'lmx':
                continue
            h = self._incorporate_zoom(v['mx_h'], lowest_max_zoom - zoom)
            w = self._incorporate_zoom(v['mx_w'], lowest_max_zoom - zoom)

            c = math.ceil(w / float(til_wid))
            r = math.ceil(h / float(til_hei))
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
            'max_zoom': lowest_max_zoom,
            'pgs': pgs
        }
        return self.data[zoom]

    def _get_max_zoom_level(self, iwid, ihei, twid, thei):
        largest_dim = iwid if iwid > ihei else ihei
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
