About
=====

This project tries to port some functionality of the //PAW Server//
(http://paw-android.fun2code.de/) to the bottle webframework.

Current functionality:

- SMS threads
- Send SMS


Install
=======

Run `./install.sh`


Start service
=============

Start script in SL4A.


Forward port on USB connection
==============================

::

    adb forward tcp:8080 tcp:8080


Remote debugging
================

Start a server in SL4A/Interpreters/Menu, look up the port in
SL4A notifications and forward the port::

    adb shell am start -a com.googlecode.android_scripting.action.LAUNCH_SERVER -n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher
    adb forward tcp:51943 tcp:51943
    export AP_PORT=51943
    python run_droidbottle.py
