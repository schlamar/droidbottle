#!/bin/bash
bash install.sh
adb shell am start -a com.googlecode.android_scripting.action.LAUNCH_FOREGROUND_SCRIPT -n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher -e com.googlecode.android_scripting.extra.SCRIPT_PATH /sdcard/sl4a/scripts/run_droidbottle.py
adb forward tcp:8080 tcp:8080
sleep 13
open http://localhost:8080/
