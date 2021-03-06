"""
https://gist.github.com/slowkow/8101481
Kamil Slowikowski
December 24, 2013
Read GFF/GTF files. Works with gzip compressed files and pandas.
    http://useast.ensembl.org/info/website/upload/gff.html
"""

from collections import defaultdict
import gzip
import re
import tempfile
import urllib

import pandas

from mupit.util import is_url

GTF_HEADER  = ['seqname', 'source', 'feature', 'start', 'end', 'score',
               'strand', 'frame']
R_SEMICOLON = re.compile(r'\s*;\s*')
R_COMMA     = re.compile(r'\s*,\s*')
R_KEYVALUE  = re.compile(r'(\s+|\s*=\s*)')

def convert_gtf(path):
    """Open an optionally gzipped GTF file and return a pandas.DataFrame.
    """
    # Each column is a list stored as a value in this dict.
    result = defaultdict(list)
    
    for i, line in enumerate(lines(path)):
        for key in line.keys():
            # This key has not been seen yet, so set it to None for all
            # previous lines.
            if key not in result:
                result[key] = [None] * i
        
        # Ensure this row has some value for each column.
        for key in result.keys():
            result[key].append(line.get(key, None))
    
    return pandas.DataFrame(result)

def lines(path):
    """Open an optionally gzipped GTF file and generate a dict for each line.
    """
    
    fn_open = gzip.open if path.endswith('.gz') else open
    
    if is_url(path):
        # if the path refers to a URL, download the file first
        temp = tempfile.NamedTemporaryFile()
        urllib.urlretrieve(path, temp.name)
        path = temp.name
    
    with fn_open(path) as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            else:
                yield parse(line)

def parse(line):
    """Parse a single GTF line and return a dict.
    """
    result = {}
    
    fields = line.rstrip().split('\t')
    
    for i, col in enumerate(GTF_HEADER):
        result[col] = _get_value(fields[i])
    
    # INFO field consists of "key1=value;key2=value;...".
    infos = [x for x in re.split(R_SEMICOLON, fields[8]) if x.strip()]
    
    for i, info in enumerate(infos, 1):
        # It should be key="value".
        try:
            key, _, value = re.split(R_KEYVALUE, info, 1)
        # But sometimes it is just "value".
        except ValueError:
            key = 'INFO{}'.format(i)
            value = info
        # Ignore the field if there is no value.
        if value:
            result[key] = _get_value(value)
    
    return result

def _get_value(value):
    if not value:
        return None
    
    # Strip double and single quotes.
    value = value.strip('"\'')
    
    # Return a list if the value has a comma.
    if ',' in value:
        value = re.split(R_COMMA, value)
    # These values are equivalent to None.
    elif value in ['', '.', 'NA']:
        return None
    
    return value
