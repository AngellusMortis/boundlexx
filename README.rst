Boundlexx
=========

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


:License: MIT

`Changelog <CHANGELOG.rst>`_
----------------------------

Requirements
------------

This project is configured to work with Docker inside of VS Code using the
Remote Containers extension. It is recommend to use those. So make sure you have:

* `Docker`_
* `VS Code`_ with the `Remote Containers extension`_.
* MacOSX version of Boundless installed somewhere. You can use `steamcmd`_ to install it via the following command:

   .. code-block:: bash
      steamcmd +@sSteamCmdForcePlatformType macos +login username +force_install_dir /path/to/install +app_update 324510 -beta testing validate +quit

* `Boundless Icon Renderer`_ set up and ran if you want to import item images into Boundlexx

.. _Docker: https://docs.docker.com/get-docker/
.. _VS Code: https://code.visualstudio.com/
.. _Remote Containers extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
.. _steamcmd: https://developer.valvesoftware.com/wiki/SteamCMD
.. _Boundless Icon Renderer: https://forum.playboundless.com/t/icon-renderer/55879

Setup
-----

#. Clone the repo.
#. Copy `docker-compose.override.example.yml` to `docker-compose.override.yml`
   and update the path you your local Boundless install
#. Then open the `boundlexx` folder in VS Code.
#. Ensure the extension "Remote - Containers" (ms-vscode-remote.remote-containers) is installed.
#. You should be prompted to "Reopen in Container". If you are not, run the
   "Remote-Containers: Reopen in Container" from the Command Palette
   (`View -> Command Palette...` or `Ctrl+Shift+P`)
#. VS Code will now build the Docker images and start them up. When it is
   done, you should see a normal VS Code Workspace
#. Go to http://127.0.0.1:8000 in your Web browser and click "Sign In".
   Then sign in with Discord or Github
#. Back in VS Code, run the command "Tasks: Run Task" and then "Boundlexx: Make Superuser".
#. Enter the username for your user when prompted.
#. Repeat "Tasks: Run Task" for the "Boundlexx: Ingest Game Data" and "Boundlexx: Create Game Objects" tasks.
