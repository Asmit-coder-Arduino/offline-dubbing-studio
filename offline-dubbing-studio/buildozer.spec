[app]
title = Offline Video Dubbing Studio
package.name = offlinedubber
package.domain = org.offlinedubber

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,so,db,json,txt,xml

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd,pillow,ffpyplayer,pyjnius,android,openssl,sqlite3

orientation = portrait, landscape

osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_path =
android.sdk_path =
android.ant_path =

android.accept_sdk_license = True

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, RECORD_AUDIO, CAMERA, FOREGROUND_SERVICE, WAKE_LOCK

android.features = android.hardware.microphone

android.gradle_dependencies = 'androidx.appcompat:appcompat:1.6.1', 'com.google.android.material:material:1.9.0'

android.enable_androidx = True

android.add_jars =

android.add_src =

android.add_libs_armeabi_v7a =
android.add_libs_arm64_v8a =

android.entrypoint = org.kivy.android.PythonActivity

android.apptheme = "@style/AppTheme"

android.meta_data =

android.services = DubbingService:utils/background_service.py:foreground

android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
