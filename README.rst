============================
BYCEPS Whereabouts Extension
============================

This is a BYCEPS_-based whereabouts extension for the Verbleiber client.

The Verbleiber system allows organizers at our LANresort_ (and
presumably NorthCon_) events to log their presence so other organizers
can locate them more easily if they are needed.

Users of the system access USB-based hardware clients connected to mini
computers, authenticating via RFID transponders and specifying their new
location at the press of one of multiple buttons.

This repository contains code that extends the BYCEPS_ LAN party
platform to provide the backend as well as a organizers-only web UI for
said system.

Development started in mid-May 2022; just days before LANresort_ 2022,
the party where it was deployed for the first time, with great success.

.. _BYCEPS: https://byceps.nwsnet.de/
.. _LANresort: https://www.lanresort.de/
.. _NorthCon: https://www.northcon.de/


Installation
============

To integrate this with BYCEPS:

- Drop the code into a BYCEPS installation.
- Register the blueprints (in ``byceps/blueprints/blueprints.py``):

  - admin blueprint: ``admin.whereabouts`` to URL path ``/admin/whereabouts``

  - API blueprint: ``api.v1.whereabouts`` to URL path ``/api/v1/whereabouts``

- Link to the admin URL paths in the admin UI's respective navigation.


Author
======

The BYCEPS whereabouts extension was created, and is developed and
maintained, by Jochen Kupperschmidt.


License
=======

The BYCEPS whereabouts extension is licensed under the `BSD 3-Clause
"New" or "Revised" License
<https://choosealicense.com/licenses/bsd-3-clause/>`_.

The license text is provided in the `LICENSE <LICENSE>`_ file.
