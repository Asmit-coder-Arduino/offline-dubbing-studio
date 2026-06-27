[app]
title = Offline Video Dubbing Studio
package.name = offlinedubber
package.domain = org.offlinedubber

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json,txt,xml

version = 1.0.0

requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,pyjnius,android,openssl,sqlite3,plyer

orientation = portrait

fullscreen = 0
android.archs = arm64-v8a

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

android.accept_sdk_license = True

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, RECORD_AUDIO, FOREGROUND_SERVICE, WAKE_LOCK

android.features = android.hardware.microphone

android.enable_androidx = True

android.entrypoint = org.kivy.android.PythonActivity

android.meta_data =

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
