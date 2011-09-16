#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from lxml import etree
from datetime import timedelta
from optparse import OptionParser


class Stat(object):

    def __init__(self, real_delta, effective_delta):
        self.real_time = real_delta
        self.effective_time = effective_delta

    def inc(self, real_delta, effective_delta):
        self.real_time += real_delta
        self.effective_time += effective_delta

    def __repr__(self):
        s = "real: %s, effective: %s" % (self.real_time, self.effective_time)
        return s


def parse_opts():
    parser = OptionParser()

    parser.add_option("", "--xml", action="store",
        dest="xml_file", help="report in XML format", metavar="FILE")

    options, args = parser.parse_args()

    if options.xml_file is None:
        parser.error("XML file required.")

    return options


def get_calltime(duration):
    columns = duration.count(':')

    if columns == 1:
        m, s = duration.split(':')
        delta = timedelta(minutes=int(m), seconds=int(s))
    elif columns == 2:
        h, m, s = duration.split(':')
        delta = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    else:
        raise Exception('Unexpected call duration format: %s', duration)

    return delta


def main():
    options = parse_opts()

    in_calls_stat = dict()
    out_calls_stat = dict()

    in_total = Stat(timedelta(0), timedelta(0))
    out_total = Stat(timedelta(0), timedelta(0))

    tree = etree.parse(options.xml_file)
    ds = tree.find('ds')
    owners_number = '+' + ds.attrib.get('n')
    info = ds.findall('i')

    for i in info:

        number = i.attrib.get('n')
        #print >>sys.stderr, "%s, %i" % (number, len(number))
        source = i.attrib.get('s')

        if len(number) > 0 and source == u'Телеф.':

                real_duration = i.attrib.get('du')
                effective_duration = i.attrib.get('dup')

                real_delta = get_calltime(real_duration)
                effective_delta = get_calltime(effective_duration)

                if number.startswith('<--'):
                    number = number[3:]

                    if len(number) == 0: number = "Unknown     "

                    if in_calls_stat.has_key(number):
                        in_calls_stat[number].inc(real_delta, effective_delta)
                    else:
                        in_calls_stat[number] = Stat(real_delta, effective_delta)

                    in_total.inc(real_delta, effective_delta)
                else:
                    if out_calls_stat.has_key(number):
                        out_calls_stat[number].inc(real_delta, effective_delta)
                    else:
                        out_calls_stat[number] = Stat(real_delta, effective_delta)

                    out_total.inc(real_delta, effective_delta)

    print
    print "Owner's number is %s" % owners_number

    print
    print "Incoming calls:"
    print
    print "Total %s" % in_total
    print

    for key, value in in_calls_stat.items():
        print "\"%s\" -- %s" % (key, value)


    print
    print "Outgoing calls:"
    print
    print "Total %s" % out_total
    print

    for key, value in out_calls_stat.items():
        print "\"%s\" -- %s" % (key, value)

    print


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print >>sys.stderr, "Failed: %s" % e
        sys.exit(-1)
