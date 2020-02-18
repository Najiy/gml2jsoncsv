#!/usr/bin/env python

    # """
    # Converts ALL GraphML file in the directory into json and csv files
    # Usage:
    # >>> python gml2other.py
    # """

import sys
import json
import re
from os import listdir
from os.path import isfile, join
import os

# This is critical for the algorithm, the headings need to include all properties of nodes and edges(links) for it to properly work.

node_headings = ['id','label', 'Country', 'Longitude', 'Latitude', 'Internal','type', 'doubted', 'geocode_append', 'geocode_country', 'geocode_id', 'x','y']
edge_headings = ['source', 'target', 'value','hyperedge','LinkLabel', 'LinkType', 'LinkNote', 'LinkSpeed', 'LinkSpeedUnits', 'LinkSpeedRaw', 'LinkStatus','description']

def gml_sub(blob):

    lines = []
    for line in blob.split('\n'):
        line = line.strip()
        lines.append(line)

    # print(lines)
    blob = "\n".join(lines)
    # print("blob", blob)

    blob = blob.replace('\n\n', '\n')
    blob = blob.replace(']\n', '},\n')
    blob = blob.replace('[\n', '{')
    blob = blob.replace('\n{', '\n    {')
    for s in node_headings + edge_headings:
        # blob = blob.replace(s, '"%s":' % s)
        blob = re.sub(r'([\s\{])(%s\s)' % s, r'\1"%s":' % s, blob)
    blob = blob.replace('\n"', ', "')
    blob = blob.replace('\n}', '}')
    blob = re.sub('\[\"', 'hello', blob)
    blob = re.sub(r'([0-9])(")', r'\1,"', blob)
    blob = re.sub(r'""', r'","', blob)

    return blob.strip('\n')


def json_to_csv(json, remove_without_location = 'y'):
    lines = []

    csv_nodes = json['nodes']

    lines.append("lat,lon,date,city,country,hyperedge\n")
    for node in csv_nodes:
        # print(node)
        if remove_without_location == 'y':
            if node.get('Latitude',False) or node.get('Longitude',False):
                lines.append("%s,%s,%s,%s,%s,%s\n"%(node.get('Latitude',0), node.get('Longitude', 0), node.get('Date', 'none'),node.get('label', 'none'),  node.get('Country', 'none'), node.get('hyperedge',0)))
        else:
            lines.append("%s,%s,%s,%s,%s,%s\n"%(node.get('Latitude',0), node.get('Longitude', 0), node.get('Date', 'none'),node.get('label', 'none'),  node.get('Country', 'none'), node.get('hyperedge', 0)))

    # print("csv nodes", lines)
    # print(lines)

    return lines

def main(graphfile):
    # """
    # Converts all GraphML file in a directory to json and csv
    # Usage:
    # >>> python convert.py mygraph.gml
    # """

    remove_without_location = raw_input("remove nodes without locaton data for csv? y/n: ")

    all_files = [f for f in listdir(graphfile) if isfile(join(graphfile, f)) and '.gml' in f]
    print(all_files)
    
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    if not os.path.exists('./json'):
        os.mkdir('./json')
    if not os.path.exists('./csv'):
        os.mkdir('./csv')
    if not os.path.exists('./logs/nodes'):
        os.mkdir('./logs/nodes')
    if not os.path.exists('./logs/edges'):
        os.mkdir('./logs/edges')


    err_count = 0
    succ_count = 0

    with open('./logs/errors.txt', 'w+') as eout:
        for each_file in all_files:
            try:
                with open(each_file, 'r') as f:
                    blob = f.read()
                    blob = re.sub('node \[', '_NODE_ [', blob)
                    blob = re.sub('edge \[','_EDGE_ [', blob)
                blob = ''.join(blob.split('_NODE_')[1:])
                nodes = re.split('_EDGE_',blob)[0]
                edges = ''.join(re.split('_EDGE_', blob)[1:]).strip().rstrip(']')

                # if log == 'y':

                path_nodes = './logs/nodes/'+each_file.replace('.gml', '.nodes')
                print(" writing to %s"% path_nodes)
                with open(path_nodes, 'w+') as fout:
                    fout.write(nodes)

                path_edges = './logs/edges/'+each_file.replace('.gml', '.edges')
                print(" writing to %s" % path_edges)
                with open(path_edges, 'w+') as fout:
                    fout.write(edges)

                nodes = gml_sub(nodes)
                edges = gml_sub(edges)

                out_json = ''
                out_json += '{\n  "nodes":['
                out_json += nodes.rstrip(',')
                out_json += '  ],\n  "edges":['
                out_json += '    ' + edges.rstrip(',')
                out_json += '  ]\n}\n'

                # print(out_json)

                path_json = './json/'+each_file.replace('.gml', '.json')
                print(" writing to %s" % path_json)
                with open(path_json, 'w+') as fout:
                    fout.write(out_json)

                # print(out_json)
                # raw_input()
                j_data = json.loads('{}')
                try:
                    j_data = json.loads(out_json)
                except Exception as identifier:
                    print(out_json)
                

                c_data = json_to_csv(j_data, remove_without_location)
                path_csv = './csv/'+each_file.replace('.gml', '.csv')
                print(" writing to %s" % path_csv)
                with open(path_csv, 'w+') as fout:
                    fout.writelines(c_data)
                print("")
                succ_count = succ_count + 1
            except Exception as identifier:
                err_count = err_count + 1
                eout.writelines('%s failed\n'% each_file)
                print('failed to convert %s\n' % each_file)
    print("\n %s failed (check './logs/errors.txt' for failed conversions)" % err_count)
    print(" %s DONE" % succ_count)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        main(sys.argv[1])
    else:
        main('./')