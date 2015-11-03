#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from qiniu.auth import Auth
from qiniu import BucketManager
from qiniu import put_data, put_file, put_stream
from conf.store_config import *

q = Auth(ACCESS_KEY, SECRET_KEY)
bucket_instance = BucketManager(q)

try:
    from urllib.parse import urljoin
    from urllib.request import urlopen, Request
except ImportError:
    from urlparse import urljoin
    from urllib2 import urlopen, Request


def get_up_token(file_name):
    """生成上传凭证.

        :parameter file_name 文件名
    """

    up_token = q.upload_token(BUCKET_NAME, file_name, expires=UNIX_TIME_TTL)
    return up_token


def put_up_datum(file_path, key, kind="file"):
    """上传资料, 三种模式: data, file, stream

        :parameter file_path
        :parameter key
        :parameter kind
    """

    token = q.upload_token(BUCKET_NAME, key)
    if kind == "data":
        ret, info = put_data(token, key, file_path)
    elif kind == "stream":
        ret, info = put_stream(token, key, file_path)
    else:
        mime_type = "text/plain"
        ret, info = put_file(token, key, file_path, mime_type=mime_type, check_crc=True)

    return ret, info


def get_shift_rs_url(file_info, bucket=None):
    """生成带Token凭证的url地址.

        :parameter file_info 文件名[?imageView2/1/w/200/h/200]
        :parameter bucket
    """

    if not bucket:
        bucket = BUCKET_DOMAIN

    base_url = 'http://%s/%s' % (bucket, file_info)
    private_url = q.private_download_url(base_url, expires=UNIX_TIME_TTL)

    return private_url


def get_public_dl_url(file_name, suffix=None):
    """公共空间：下载地址.

        :parameter file_name
        :parameter suffix
    """

    if not file_name:
        raise ValueError
    if suffix:
        file_name += suffix

    base_url = PUBLIC_BUCKET_DOMAIN or 'http://%s.qiniudn.com/' % PUBLIC_BUCKET_NAME
    return urljoin(base_url, file_name)


def del_remote_dl_key(key, bucket=None):
    """删除文件.

        :parameter key
        :parameter bucket
    """

    if not bucket:
        bucket = BUCKET_DOMAIN

    ret, err = bucket_instance.delete(bucket, key)
    return err
