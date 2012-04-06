runtogether.py
==============

A utility command to start other commands in the background.

If one of them dies with an error, all of them are terminated.

``Ctrl-C`` terminates them as well.


Why?
----

This program relieves you of ugly tasks like implementing ``trap`` in shell scripts or fighting against subprocess absorbing ``Ctrl-C`` control.

License
-------

MIT.

Example
-------

::

    #!/usr/bin/env python

    commands = [
        "runhaskell Testserver.hs",
        "python -m SimpleHTTPServer 7357",
    ]

    if __name__ == '__main__':
        import runtogether
        runtogether.runtogether(commands)
