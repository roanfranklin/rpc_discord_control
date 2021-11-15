#!/bin/bash

export QT_DEBUG_PLUGINS=1
export QT_PLUGIN_PATH=/usr/lib/qt/plugins

cd /remf/share/rpc_discord_control
./rpc_discord_control.py