#!/bin/sh
# echo needs to be executed by a DD with login to master

CACHEDIR=/var/cache/teammetrics/mboxes
mkdir -p $CACHEDIR

LISTS="debian-accessibility \
       debian-amd64 \
       debian-arm \
       debian-blends debian-custom \
       debian-boot \
       debian-ctte \
       debian-curiosa \
       debian-derivatives \
       debian-devel \
       debian-announce \
       debian-games \
       debian-edu \
       debian-embedded \
       debian-enterprise \
       debian-firewall \
       debian-gis \
       debian-i18n \
       debiab-isp \
       debian-med \
       debian-science"

for list in $LISTS ; do
	rsync -a master.debian.org:/home/debian/lists/$list $CACHEDIR
done

rsync -a $CACHEDIR/* dbmed:$CACHEDIR
