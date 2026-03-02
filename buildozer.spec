[app]

# Application title
title = Metro Tetris

# Package name
package.name = metrotetris

# Package domain (needed for android/ios)
package.domain = org.larosa

# Source code where the main.py is located
source.dir = .

# Source files to include (all file types used by runtime)
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,wav,ogg,mp3,md

# Version
version = 0.1

# Application requirements
# FIXED VERSIONS: Pin Cython 0.29.x and pyjnius 1.6.1 to avoid Cython 3.x breaking changes
# Cython 3.x removed 'long' type causing pyjnius compilation failures in Python 3
requirements = python3,kivy,Cython==0.29.36,pyjnius==1.6.1

# Supported orientations: landscape, portrait, portrait-reverse, landscape-reverse
orientation = portrait

# Fullscreen mode (0=False, 1=True)
fullscreen = 0

# Android specific
# Keep all android.* keys in [app] section so Buildozer reads them correctly

# Android API to use
android.api = 31

# Minimum API required
android.minapi = 21

# Android SDK version to use (DEPRECATED - buildozer ignores this, use android.api instead)
# android.sdk = 31

# Android NDK API level
android.ndk_api = 21

# Android NDK version to use
android.ndk = 25b

# Permissions
android.permissions = VIBRATE

# Features
android.features = 

# App icon
#icon.filename = %(source.dir)s/data/icon.png

# Presplash
#presplash.filename = %(source.dir)s/data/presplash.png

# Android architecture (compile only arm64-v8a for speed, supports most devices)
android.archs = arm64-v8a

# Force arm64-v8a only - do NOT add additional architectures
# This prevents armeabi-v7a compilation which is incompatible with current setup

# SDK and NDK paths: commented out to use buildozer defaults (CI-friendly)
# android.sdk_path = /home/xavi_delgado/.buildozer/android/platform/android-sdk
# android.ndk_path = /home/xavi_delgado/.buildozer/android/platform/android-ndk-r25b

# Accept SDK licenses automatically
android.accept_sdk_license = True

# Use NDK build for faster compilation
android.use_ndk_build = 0

# CRITICAL FIX: Enable pyjnius setup.py execution to generate config.pxi
# Required for Cython compilation of pyjnius 1.4+
# If set to 1 (ignore setup.py), Cython fails: "'config.pxi' not found"
p4a_ignore_setuppy = 0

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1
