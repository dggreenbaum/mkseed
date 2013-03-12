#mkseed

mkseed is a simple generator for Debian preseed files.

## Dependancies

* jinja2

## Example

    from mkseed.generator import *

    # Make an instance
    gen = generator("IP", "NETMAKSK", "GATEWAY")

    # Print the file to your console.
    gen.print()

    # Save the file to disk.
    gen.save("/path/to/file.ext")

    # Upload the file via FTP.
    gen.publish("ftp.host.com", "username", "pa$$word", "relative/path/to/file.ext")