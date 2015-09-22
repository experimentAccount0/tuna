Installation of Tuna
====================

Tuna is built as a Python package, and to have it working in your system, you need:

- The code for Tuna in a directory inside one of the locations listed in your environment's $PYTHONPATH.
   
- The following third-party Python modules must be installed:

- Optionally, if a MySQL server is installed, Tuna will use it to store cross-references between its numpy arrays' hashes.

In the current version, Tuna is not yet part of PyPI, but this should be corrected very soon. Therefore, the installation procedure consists of cloning the repository and using the setup.py script directly.

Dependencies
------------

Tuna depends on the following packages, and will install them if they are not yet installed in your system (or virtual environment):

   #. `Astropy <http://www.astropy.org/>`_
     
   #. `Matplotlib <http://matplotlib.org/>`_

   #. `Mpyfit <https://github.com/evertrol/mpyfit>`_
      
   #. `Numpy <http://www.numpy.org/>`_
      
   #. `Psutil <https://github.com/giampaolo/psutil>`_
      
   #. Pyfits
      
   #. Pyqt4
      
   #. Scipy
      
   #. Sympy
      
   #. ZeroMQ

Virtualenv
----------

We highly recommend using Python's virtual environments to encapsulate all dependencies of Tuna in a single namespace, and avoid conflicting with other Python software in your system.

To create a virtual environment, the command is::

  virtualenv <path>/<name>

To use a virtual environment, the command is::

  source <path>/<name>/bin/activate

Once activated, the Python interpreter and the modules it uses are loaded from the virtual environment. Also, packages installed using pip are installed inside the virtual environment. In this way, it is very easy to have multiple Python packages installed in the same system, without conflicts, as long as each package is in its own virtual environment.

Also, packages installed by downloading the code from github (such as Mpyfit), work by simply cloning the repo inside the virtualenv directory.

Python versions
---------------

Tuna is compatible with Python 2 and Python 3, but it is developed under Python 3, and if eventually we have to choose between remaining compatible with Python 2 or including an incompatible feature, we will choose the feature. Therefore, we highly recommend that Tuna be installed and ran using Python 3.

Linux installation - with virtualenv
------------------------------------

This is a step-by-step guide to installing Tuna in Fedora 21. It uses Python 3 and virtual environments. We install in the directory ~/vtuna, so if you install in another directory, please adjust your commands accordingly.

#. Create the virtual environment that will contain Tuna::

     ~ $ virtualenv -p python3 vtuna

#. Activate the virtual environment::

     ~ $ cd vtuna
     
     vtuna $ source bin/activate

#. Obtain the source code for Tuna::

     (vtuna)vtuna $ git clone https://github.com/rcbrgs/tuna.git

#. Install the package::

     (vtuna)vtuna $ python tuna/setup.py install

   This could take some time to install, since some of the packages are large (dozens of MB).

#. Use Tuna::

     (vtuna)vtuna $ ipython
     Python 3.4.1 (default, Nov  3 2014, 14:38:10)
     Type "copyright", "credits" or "license" for more information.

     IPython 4.0.0 -- An enhanced Interactive Python.
     ?         -> Introduction and overview of IPython's features.
     %quickref -> Quick reference.
     help      -> Python's own help system.
     object?   -> Details about 'object', use 'object??' for extra details.

     In [1]: import tuna

     In [2]:

Using Tuna once it has already been installed in a virtual environment
----------------------------------------------------------------------

Once Tuna is installed, you must always load the virtual environment where it resides before using it. The commands are::

  ~ $ cd vtuna
  vtuna $ source bin/activate
  (tuna)tuna $ ipython
  Python 3.4.1 (default, Nov  3 2014, 14:38:10)
  Type "copyright", "credits" or "license" for more information.

  IPython 4.0.0 -- An enhanced Interactive Python.
  ?         -> Introduction and overview of IPython's features.
  %quickref -> Quick reference.
  help      -> Python's own help system.
  object?   -> Details about 'object', use 'object??' for extra details.

  In [1]: import tuna

  In [2]:

Of course, if you created your virtual environment in a directory other than ~/tuna, you should adjust your commands accordingly.

Linux installation - without virtualenv
---------------------------------------

This is a step-by-step guide to installing Tuna in Fedora 21. It uses Python 3.

#. Obtain the source code for Tuna::

     $ git clone https://github.com/rcbrgs/tuna.git

#. Install the package::

     $ python tuna/setup.py install

   This could take some time to install, since some of the packages are large (dozens of MB).

#. Use Tuna::

     $ ipython
     Python 3.4.1 (default, Nov  3 2014, 14:38:10)
     Type "copyright", "credits" or "license" for more information.

     IPython 4.0.0 -- An enhanced Interactive Python.
     ?         -> Introduction and overview of IPython's features.
     %quickref -> Quick reference.
     help      -> Python's own help system.
     object?   -> Details about 'object', use 'object??' for extra details.

     In [1]: import tuna

     In [2]: