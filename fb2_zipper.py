#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import argparse
from xml.dom import minidom

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", dest="folder", help="folder for search books")
    parser.add_argument("-b", "--book", dest="book", help="handle one book")
    parser.add_argument("-r", "--remove", action="store_true", help="remove old books")
    args = parser.parse_args()
    if args.book != None:
        folder_hndl(args.book, args.remove)
    elif args.folder != None:
        folder_hndl(args.folder, args.remove)
    else:
        print("One of folowing argument is required: --book, --folder", file=sys.stderr)


def folder_hndl(path, remove=False):
    if os.path.isfile(path):
        flag = False
        print("\tprocessing file: %s" % path)
        if path[-4:] == ".fb2":
            flag = fb2_hndl(path)
        elif path[-8:] == ".fb2.zip":
            flag = fb2_zip_hndl(path)
            
        if remove and flag:
            print("\t\tremoved file")
            os.remove(path)
        else:
            print("\t\tnot removed file")
    else:
        print("scan folder: %s" % path)
        file_list = os.listdir(path)
        for file in file_list:
            file_path = os.path.join(path, file)
            folder_hndl(file_path, remove)
        print("\n")


def fb2_hndl(file_path):
    status = True
    try:
        dom = minidom.parse(file_path)
    except:
        print("\t\tERROR: Failed to parse file")
        status = False
    else:
        dir_path = os.path.split(file_path)[0]
        book_name = fb2_get_book_name(dom)
        if(book_name != None):
            book_path = os.path.join(dir_path, book_name) + ".zip"
            if book_path != file_path:
                zf = zipfile.ZipFile(book_path, 'w', zipfile.ZIP_DEFLATED)
                zf.writestr(book_name, dom.toxml())
                zf.close()
                status = True
            else:
                print("\t\tcorrect file already exists")
                status = False
        else:
            status = False
    return status


def fb2_zip_hndl(file_path):
    status = True
    if zipfile.is_zipfile(file_path):
        zf = zipfile.ZipFile(file_path, 'r')
        dir_path = os.path.split(file_path)[0]        
        for fname in zf.namelist():
            if fname[-4:] == ".fb2":
                print("\t\tfind fb2 file: %s" % fname)
                book_zf = zf.open(fname, 'r')
                try:
                    dom = minidom.parse(book_zf)
                except:
                    print("\t\tERROR: Failed to parse file")
                    status = False
                else:
                    book_name = fb2_get_book_name(dom)
                    if(book_name != None):
                        book_path = os.path.join(dir_path, book_name) + ".zip"
                        if book_path != file_path:
                            nzf = zipfile.ZipFile(book_path, 'w', zipfile.ZIP_DEFLATED)
                            nzf.writestr(book_name, dom.toxml())
                            nzf.close()
                            status = True
                        else:
                            print("\t\tcorrect file already exists")
                            status = False
                    else:
                        status = False
        zf.close()
    else:
        status = False
    return status


def fb2_get_book_name(dom):
    title_info_node = dom.getElementsByTagName("title-info")

    author_node = title_info_node[0].getElementsByTagName("author")

    first_name_node = author_node[0].getElementsByTagName("first-name")
    last_name_node = author_node[0].getElementsByTagName("last-name")

    book_title_node = title_info_node[0].getElementsByTagName("book-title")

    book_name = xml_get_text(book_title_node[0].firstChild)
    first_name = xml_get_text(first_name_node[0].firstChild)
    last_name = xml_get_text(last_name_node[0].firstChild)

    if book_name != None and first_name != None and last_name != None:
        book_name = book_name.replace("\\", ".")
        book_name = book_name.replace("/", ".")
        book_name = book_name.replace("|", ".")
        return first_name + " " + last_name + " - " + book_name + ".fb2"
    else:
        return None
    
                             
                
def xml_get_text(node):
    if node is None:
         return None
    else:
        return node.nodeValue
       


if __name__ == "__main__":
    main()















