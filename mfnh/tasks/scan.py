from . import scan_movies, scan_tv
from ..db import ContentType, Root


def scan(sess):
    for root in sess.query(Root).all():
        if root.content_type == ContentType.MOVIES:
            scan_movies.scan_root(sess, root)
        # elif root.content_type == ContentType.TV:
        #     scan_tv.scan_root(sess, root)
