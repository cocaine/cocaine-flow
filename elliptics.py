#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

sys.path.insert(0, "/usr/lib/")
sys.path.insert(0, "./.libs/")
import libelliptics_python

class NodeStatus(libelliptics_python.dnet_node_status):
    def __repr__(self):
        return "<NodeStatus nflags:%x, status_flags:%x, log_mask:%x>" % (self.nflags, self.status_flags, self.log_mask)


class Id(libelliptics_python.elliptics_id):
    """
     Elliptics ID wrapper
     It has 2 constructors:
         Id()
         Id(list_id, group type)

     list_id - list of 64 bytes, id of the object itself
     group - group ID of the object
     type - column
     """
    pass


class Range(libelliptics_python.elliptics_range):
    """
     Structure that describes range request
     start, end - IDs of the start and the end of the range
     offset, size - offset to read from and size of bytes to read, applied for each key
     cflags - command flags like locking, checksum and so on (default is 0)
     ioflags - command IO flags (default is 0)
     group - group ID of the object
     type - column
     """
    pass


class Logger(libelliptics_python.elliptics_log_file):
    """
     Logger, that needed in Node constructor
     Constructor takes 2 arguments: log file name (default is "/dev/stderr")
     and log mask (default is 40)
     """
    log_file_name = ""
    log_mask = ""

    def __init__(self, log_file_name="/dev/stderr", log_mask=40):
        """
          log_file_name - name of the log file, default value is "/dev/stderr"
          log_mask - logging mask, default value is 40. Log mask bits:
              0 - NOTICE
              1 - INFO
              2 - TRANSACTIONS
              3 - ERROR
              4 - DEBUG
              5 - DATA
          """
        self.log_file_name = log_file_name
        self.log_mask = log_mask
        super(Logger, self).__init__(log_file_name, log_mask)

    def log(self, message, mask=16):
        """
          log some message into elliptics log file
          message - text message
          mask - log mask, default is DEBUG (see __init__ docstring for log mask bits)
          """
        super(Logger, self).log(mask, message)

    def __repr__(self):
        return "<Logger log_file_name:\"%s\" log_mask:%x>" % (self.log_file_name, self.log_mask)


class Node(libelliptics_python.elliptics_node_python):
    """
     Main client class. Constructor takes 1 argument: Logger object
     """

    def __init__(self, log):
        """
          log - Logger object
          """
        super(Node, self).__init__(log)

    def add_remote(self, addr, port, family=2):
        """
          Add address of elliptics storage node and connect to it
          addr - storage address
          port - storage port
          family - IP protocol family: 2 for IPv4 (default value) and 10 for IPv6
          """
        super(Node, self).add_remote(addr, port, family)

    def add_groups(self, groups):
        """
          Set groups to work with
          groups - list of groups
          """
        super(Node, self).add_groups(groups)

    def get_routes(self):
        """
          Get routing table

          return value:
          list - list of node addresses
          """
        return super(Node, self).get_routes()

    def stat_log(self):
        """
          Get nodes statistics

          return value:
          string - storage nodes statistics
          """
        return super(Node, self).stat_log()

    def lookup_addr(self, *args, **kwargs):
        """
          Lookup where key should be located by its ID or key and group_id pair
          signatures:
              lookup_addr(key, group_id)
              lookup_addr(id)

          key - remote key name
          group_id - group
          id - object of Id class

          return value:
          string - node address
          """
        return super(Node, self).lookup_addr(*args, **{})

    def read_file(self, *args, **kwargs):
        """
          Read file from elliptics by name/ID
          signatures:
              read_file(key, filename, offset, size, type)
              read_file(id, filename, offset, size)

          key - remote key name
          type - column type (default is 0, 1 is reserved for metadata)
          id - object of Id class

          filename - name of local file where data will be saved
          offset - read file from this offset (default 0)
          size - number of bytes to read, 0 means whole file (default is 0)
          """
        kwargs["key"] = args[0]
        kwargs["filename"] = filename

        if (len(args) > 2):
            kwargs["offset"] = args[2]
        elif not kwargs.has_key("offset"):
            kwargs["offset"] = 0

        if (len(args) > 3):
            kwargs["size"] = args[3]
        elif not kwargs.has_key("size"):
            kwargs["size"] = 0

        if (len(args) > 4):
            kwargs["type"] = args[4]
        elif not kwargs.has_key("type"):
            kwargs["type"] = 0

        if (type(args[0]) == str):
            new_args = (kwargs["key"], kwargs["filename"], kwargs["offset"], kwargs["size"], kwargs["type"])
        else:
            new_args = (kwargs["key"], kwargs["filename"], kwargs["offset"], kwargs["size"])

        super(Node, self).read_file(*new_args, **{})

    def write_file(self, *args, **kwargs):
        """
          Write file into elliptics by name/ID
          signatures:
              write_file(key, filename, local_offset, offset, size, aflags, ioflags, type)
              write_file(id, filename, local_offset, offset, size, aflags, ioflags)

          key - remote key name
          type - column type (default is 0, 1 is reserved for metadata)
          id - object of Id class

          filename - name of local file
          local_offset - read local file from this offset (default 0)
          offset - write file from this offset (default 0)
          size - number of bytes to write, 0 means whole file (default is 0)
          aflags - command attributes flags (default is 0)
          ioflags - command IO flags (default is 0)
          """
        kwargs["key"] = args[0]
        kwargs["filename"] = filename

        if (len(args) > 2):
            kwargs["local_offset"] = args[2]
        elif not kwargs.has_key("local_offset"):
            kwargs["local_offset"] = 0

        if (len(args) > 3):
            kwargs["offset"] = args[3]
        elif not kwargs.has_key("offset"):
            kwargs["offset"] = 0

        if (len(args) > 4):
            kwargs["size"] = args[4]
        elif not kwargs.has_key("size"):
            kwargs["size"] = 0

        if (len(args) > 5):
            kwargs["aflags"] = args[5]
        elif not kwargs.has_key("aflags"):
            kwargs["aflags"] = 0

        if (len(args) > 6):
            kwargs["ioflags"] = args[6]
        elif not kwargs.has_key("ioflags"):
            kwargs["ioflags"] = 0

        if (len(args) > 7):
            kwargs["type"] = args[7]
        elif not kwargs.has_key("type"):
            kwargs["type"] = 0

        if (type(args[0]) == str):
            new_args = (kwargs["key"], kwargs["filename"], kwargs["local_offset"], kwargs["offset"], kwargs["size"],
                        kwargs["aflags"], kwargs["ioflags"], kwargs["type"])
        else:
            new_args = (kwargs["key"], kwargs["filename"], kwargs["local_offset"], kwargs["offset"], kwargs["size"],
                        kwargs["aflags"], kwargs["ioflags"])

        super(Node, self).read_file(*new_args, **{})

    def read_data(self, *args, **kwargs):
        """
          Read data from elliptics by name/ID
          signatures:
              read_data(key, offset, size, aflags, ioflags, type)
              read_data(id, offset, size, aflags, ioflags)

          key - remote key name
          type - column type (default is 0, 1 is reserved for metadata)
          id - object of Id class

          offset - read file from this offset (default 0)
          size - number of bytes to read, 0 means whole file (default is 0)
          aflags - command attributes flags (default is 0)
          ioflags - command IO flags (default is 0)

          return value:
          string - key value content
          """
        kwargs["key"] = args[0]

        if (len(args) > 1):
            kwargs["offset"] = args[1]
        elif not kwargs.has_key("offset"):
            kwargs["offset"] = 0

        if (len(args) > 2):
            kwargs["size"] = args[2]
        elif not kwargs.has_key("size"):
            kwargs["size"] = 0

        if (len(args) > 3):
            kwargs["aflags"] = args[3]
        elif not kwargs.has_key("aflags"):
            kwargs["aflags"] = 0

        if (len(args) > 4):
            kwargs["ioflags"] = args[4]
        elif not kwargs.has_key("ioflags"):
            kwargs["ioflags"] = 0

        if (len(args) > 5):
            kwargs["type"] = args[2]
        elif not kwargs.has_key("type"):
            kwargs["type"] = 0

        if (type(args[0]) == str):
            new_args = (
            kwargs["key"], kwargs["offset"], kwargs["size"], kwargs["aflags"], kwargs["ioflags"], kwargs["type"])
        else:
            new_args = (kwargs["key"], kwargs["offset"], kwargs["size"], kwargs["aflags"], kwargs["ioflags"])

        return super(Node, self).read_data(*new_args, **{})

    def read_latest(self, key, data, offset=0, aflags=0, ioflags=0, type_=0):
        """
          Read data from elliptics by name/ID with the latest update_date in metadata
          signatures:
              read_latest(key, offset, size, aflags, ioflags, type)
              read_latest(id, offset, size, aflags, ioflags)

          key - remote key name
          type - column type (default is 0, 1 is reserved for metadata)
          id - object of Id class

          offset - read file from this offset (default 0)
          size - number of bytes to read, 0 means whole file (default is 0)
          aflags - command attributes flags (default is 0)
          ioflags - command IO flags (default is 0)

          return value:
          string - key value content
          """
        new_args = [key, data, offset, aflags, ioflags]

        if isinstance(key, basestring):
            new_args.append(type_)

        return super(Node, self).read_latest(*new_args, **{})


    def write_data(self, key, data, offset=0, aflags=0, ioflags=0, type_=0):
        """
             Write data into elliptics by name/ID
             signatures:
                 write_data(key, data, offset, aflags, ioflags, type)
                 write_data(id, data, offset, aflags, ioflags)

             key - remote key name
             type - column type (default is 0, 1 is reserved for metadata)
             id - object of Id class

             data - data to be written
             offset - write data in remote from this offset (default 0)
             aflags - command attributes flags (default is 0)
             ioflags - command IO flags (default is 0)

             return value:
             string - nodes and paths where data was stored
             """

        new_args = [key, data, offset, aflags, ioflags]

        if isinstance(key, basestring):
            new_args.append(type_)

        return super(Node, self).write_data(*new_args, **{})

    def write_metadata(self, *args, **kwargs):
        """
             Write metadata into elliptics by name/ID
             signatures:
                 write_metadata(key, aflags)
                 write_metadata(id, name, groups, aflags)

             key - remote key name
             id - object of Id class

             name - key name
             groups - groups where data was stored
             aflags - command attributes flags (default is 0)
             """
        kwargs["key"] = args[0]

        if (type(args[0]) == str):
            if (len(args) > 1):
                kwargs["aflags"] = args[1]
            elif not kwargs.has_key("aflags"):
                kwargs["aflags"] = 0
        else:
            if (len(args) > 1):
                kwargs["name"] = args[1]

            if (len(args) > 2):
                kwargs["groups"] = args[2]

            if (len(args) > 3):
                kwargs["aflags"] = args[3]
            elif not kwargs.has_key("aflags"):
                kwargs["aflags"] = 0

        if (type(args[0]) == str):
            new_args = (kwargs["key"], kwargs["aflags"])
        else:
            new_args = (kwargs["key"], kwargs["name"], kwargs["groups"], kwargs["aflags"])

        super(Node, self).write_metadata(*new_args, **{})


    def remove(self, *args, **kwargs):
        """
             Remove key by name/ID
             signatures:
                 remove(key, aflags, type)
                 remove(id, aflags, ioflags)

             key - remote key name
             type - column type (default is 0, 1 is reserved for metadata)
             id - object of Id class

             aflags - command attributes flags (default is 0)
             ioflags - IO flags (like cache)
             """
        kwargs["key"] = args[0]

        if (len(args) > 1):
            kwargs["aflags"] = args[1]
        elif not kwargs.has_key("aflags"):
            kwargs["aflags"] = 0

        if (len(args) > 2):
            kwargs["type"] = args[2]
        elif not kwargs.has_key("type"):
            kwargs["type"] = 0

        if (type(args[0]) == str):
            new_args = (kwargs["key"], kwargs["aflags"], kwargs["type"])
        else:
            new_args = (kwargs["key"], kwargs["aflags"])

        super(Node, self).remove(*new_args, **{})


    def execute(self, *args, **kwargs):
        """
             Execite server-side script
             signatures:
                 exec(id, script, binary, type)
                 exec(script, binary, type)
                 exec(key, script, binary, type)

             key - remote key name
             id - object of Id class

             script - server-side script
             binary - data for server-side script
             type - type of execution

             If execute() is called with 3 arguments script will be runned on all storage nodes.
             If id or key is specified script will be runned on one node according to key/id.

             return value:
             string - result of the script execution
             """
        return super(Node, self).execute(*args, **{})


    def exec_name(self, *args, **kwargs):
        """
             Execite server-side script by name
             signatures:
                 exec_name(id, name, script, binary, type)
                 exec_name(name, script, binary, type)
                 exec_name(key, name, script, binary, type)

             key - remote key name
             id - object of Id class

             name - server-side script name
             script - server-side script
             binary - data for server-side script
             type - type of execution

             If exec_name() is called with 3 arguments script will be runned on all storage nodes.
             If id or key is specified script will be runned on one node according to key/id.

             return value:
             string - result of the script execution
             """
        return super(Node, self).exec_name(*args, **{})


    def update_status(self, *args, **kwargs):
        """
             Update elliptics status and log mask
             signatures:
                 update_status(id, status, update)
                 update_status(addr, port, family, status, update)

             key - remote key name
             id - object of Id class

             addr - storage address
             port - storage port
             family - IP protocol family: 2 for IPv4 (default value) and 10 for IPv6
             status - new node status, object of NodeStatus class
             update - update status or just return current (default is 0)

             If update = 0 status will not be changed

             return value:
             NodeStatus - current node status
             """

        if (type(args[0]) == str):
            if (len(args) > 0):
                kwargs["addr"] = args[0]

            if (len(args) > 1):
                kwargs["port"] = args[1]

            if (len(args) > 2):
                kwargs["family"] = args[2]
            elif not kwargs.has_key("family"):
                kwargs["family"] = 2

            if (len(args) > 3):
                kwargs["status"] = args[3]
            elif not kwargs.has_key("status"):
                kwargs["status"] = NodeStatus()

            if (len(args) > 4):
                kwargs["update"] = args[4]
            elif not kwargs.has_key("update"):
                kwargs["update"] = 0
        else:
            if (len(args) > 0):
                kwargs["id"] = args[0]

            if (len(args) > 1):
                kwargs["status"] = args[1]
            elif not kwargs.has_key("status"):
                kwargs["status"] = NodeStatus()

            if (len(args) > 2):
                kwargs["update"] = args[2]
            elif not kwargs.has_key("update"):
                kwargs["update"] = 0

        if (type(args[0]) == str):
            new_args = (kwargs["addr"], kwargs["port"], kwargs["family"], kwargs["status"], kwargs["update"])
        else:
            new_args = (kwargs["key"], kwargs["status"], kwargs["update"])

        ret = super(Node, self).update_status(*new_args, **{})
        ret.__class__ = NodeStatus
        return ret


    def bulk_read(self, keys, group_id, aflags=0):
        """
             Bulk read keys from elliptics
             keys - list of keys by name
             group_id - group ID
             aflags - command attributes flags (default is 0)

             return value:
             list - list of strings, each string consists of 64 byte key, 8 byte data length and data itself
             """
        return super(Node, self).bulk_read(keys, group_id, aflags)


    def read_data_range(self, read_range):
        """
             Read keys from elliptics by range of IDs
             read_range - object of Range class

             return value:
             list - list of strings, each string consists of 64 byte key, 8 byte data length and data itself
             """
        return super(Node, self).read_data_range(read_range)


