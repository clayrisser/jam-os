#!/bin/sh

curl -Lo theme.tar.gz https://gitlab.com/risserlabs/community/firefox-sway-gnome-theme/-/archive/master/firefox-sway-gnome-theme-master.tar.gz
tar -xzvf theme.tar.gz
cd firefox-sway-gnome-theme-master
yes | bash ./scripts/auto-install.sh
cd ..
rm -rf theme.tar.gz firefox-sway-gnome-theme-master

xdg-settings set default-web-browser librewolf.desktop