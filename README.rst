Brivo
=====

Open source home brewery manger.

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style

The app is still in alpha version and requires some improvements. Soon the docs on how to install it
on Synology NAS will be available.


License
^^^^^^^

This software and all its features are and will always be free for everyone to use and enjoy.

The code in this repository is licensed under the `GNU AGPL v3 <https://www.gnu.org/licenses/agpl-3.0.de.html>`_ license with an
`common clause <https://commonsclause.com/>`_ selling exception. See `LICENSE <https://github.com/guma44/brivo/blob/develop/LICENSE>`_ for details.

The licence is based on the `LICENSE.md <https://github.com/vabene1111/recipes/blob/develop/LICENSE>`_ as the scope of
the software is similar and I have similar view on the matter.


Install on Synology
^^^^^^^^^^^^^^^^^^^

Create directories:
 * docker/brivo/log/celery
 * docker/brivo/log/redis
 * docker/brivo/log/django
 * docker/brivo/log/supervisor
 * docker/brivo/run
 * docker/brivo/web/media
 * docker/brivo/web/data
 * docker/brivo/web/redis-data

Add previliges to directories
Mount directories to Docker
Start container `guma44/brivo:latest`
network - bridge

login to shell and do:
python manage.py createsuperuser
python manage.py load_db_data