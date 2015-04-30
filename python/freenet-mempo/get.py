#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
import subprocess
import time
import os
import sys
import logging

try:
  import requests
except ImportError:
  print("pip install --user requests")
  sys.exit()

def freeget(usk, freenet):
  """
  download from freenet
  """
  return requests.get('{}{}?forcedownload&max-size=99999999'.format(freenet, usk))
  

def ensure_file(fname):
  """
  ensure a file can be written
  create any needed directories
  """
  if '/' in fname:
    dirname = fname[:fname.rindex('/')]
    subprocess.Popen(['mkdir', '-p',dirname]).wait()

def file_exists(fname):
  """
  shortcut for os.path.exists
  """
  return os.path.exists(fname)

def named_dir(revision):
  """
  get the directory name for a mempo revision
  """
  return os.path.join("mempo", "{}".format(revision))

def get_fname(fname, revision):
  """
  get output filename for a freenet resource
  """
  return os.path.join(named_dir(revision), fname)

def get_all(usk, rev, freenet):
  """
  download the entire mempo repository via freenet
  """
  log = logging.getLogger("mempo")
  log.info("\t++ downloading repo index")
  # get index text file
  data = freeget('{}/{}/index-all.txt'.format(usk, rev), freenet).text

  # split it up into lines
  for line in data.split('\n'):
    # strip whitespaces
    fname = line.replace(' ','')
    if len(fname) > 0:
      
      # ignore comments
      if fname[0] == '#':
        continue

      # obtain output filename
      # ensure it exists too
      ofname = get_fname(fname, rev)
      ensure_file(ofname)
      log.info("\t++ downloading {}".format(fname))
      # try download
      tries = 10
      while not file_exists(ofname):

        url = "{}/{}/{}".format(usk, rev, fname)
        log.debug("resource: {}".format(url))
        req = freeget(url, freenet)
        log.debug(req.status_code)

        # did the request fail?
        if req.status_code == 200:
          # we got it
          # write it out
          with open(ofname, 'w') as fd:
            fd.write(req.content)
          # next file
          break
        elif tries > 0:
          # still have tries left
          # retry download
          log.warn(' -- [{}] retry {}'.format(tries, fname))
          tries -= 1
          time.sleep(1)
          continue
        else:
          # damnit we can't download it, complain
          log.error(" !! Failed to download {}".format(fname))


from argparse import ArgumentParser as AP

def main():
  # default mempo usk
  mempo_usk='USK@oRy7ltZLJM-w-kcOBdiZS1pAA8P-BxZ3BPiiqkmfk0E,6a1KFG6S-Bwp6E-MplW52iH~Y3La6GigQVQDeMjI6rg,AQACAAE/deb.mempo.org'

  # init argparser
  ap = AP()
  ap.add_argument("--usk", default=mempo_usk, type=str, help="custom freenet address to download from (BE VERY CAREFUL)")
  ap.add_argument("--debug", action="store_const", default=False, const=True, help="enable debug output")
  ap.add_argument("--freenet", default="http://127.0.0.1:8888/", type=str, help="url of freenet proxy")
  ap.add_argument("--revision", required=True, type=int, help="freenet repo revision number")

  # parse args
  args = ap.parse_args()

  # determin log level
  lvl = args.debug and logging.DEBUG or logging.INFO

  # config logging
  logging.basicConfig(format="%(created)d -- %(name)s-%(levelname)s: %(message)s")

  # set level of mempo logger
  log = logging.getLogger("mempo")
  log.setLevel(lvl)

  # tell the user stuff
  log.info("\t--> obtaining mempo repository via freenet")
  log.warn("\t!!! This WILL take a long time")
  log.info("\t--> using freenet proxy: {}".format(args.freenet))
  log.info("\t--> using revision: {}".format(args.revision))
  
  # do it :^3
  get_all(args.usk, args.revision, args.freenet)

if __name__ == '__main__':
  main()
