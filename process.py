#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from lxml import etree
from datetime import timedelta
from optparse import OptionParser


def parse_opts():
    parser = OptionParser()

    parser.add_option("", "--xml", action="store",
        dest="xml_file", help="report in XML format", metavar="FILE")

    options, args = parser.parse_args()

    if options.xml_file is None:
        parser.error("XML file required.")

    return options


def main():
    options = parse_opts()

    in_calls_stat = dict()
    out_calls_stat = dict()

    tree = etree.parse(options.xml_file)
    ds = tree.find('ds')
    owners_number = '+' + ds.attrib.get('n')
    info = ds.findall('i')

    for i in info:

        number = i.attrib.get('n')
        source = i.attrib.get('s')

        if len(number) > 0 and source == u'Телеф.':

                duration = i.attrib.get('dup')
                colomns_count = duration.count(':')

                if colomns_count == 1:
                    m, s = duration.split(':')
                    delta = timedelta(minutes=int(m), seconds=int(s))
                elif colomns_count == 2:
                    h, m, s = duration.split(':')
                    delta = timedelta(hours=int(h), minutes=int(m),
                        seconds=int(s))
                else:
                    raise Exception('Unexpected call duration format: %s',
                        duration)

                if number.startswith('<--'):
                    number = number[3:]

                    if in_calls_stat.has_key(number):
                        in_calls_stat[number] += delta
                    else:
                        in_calls_stat[number] = delta
                else:
                    if out_calls_stat.has_key(number):
                        out_calls_stat[number] += delta
                    else:
                        out_calls_stat[number] = delta

    print
    print "Owner's number is %s" % owners_number

    print
    print "Incoming calls:"
    print

    for key, value in in_calls_stat.items():
        print "%s -- %s" % (key, value)

    print
    print "Outgoing calls:"
    print

    for key, value in out_calls_stat.items():
        print "%s -- %s" % (key, value)

    print


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print >>sys.stderr, "Failed: %s" % e
        sys.exit(-1)
