== Install ==

{{{
adb push bottle.py /sdcard/com.googlecode.pythonforandroid/extras/python/
}}}

run ./install.sh

== Forward port on USB connection ==

{{{
adb forward tcp:8080 tcp:8080
}}}
