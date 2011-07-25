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
       debian-isp \
       debian-jr \
       debian-kde \
       debian-kernel \
       debian-l10n-german \
       debian-laptop \
       debian-legal \
       debian-lex \
       debian-live \
       debian-med \
       debian-mentors \
       debian-mips \
       debian-multimedia \
       debian-newmaint \
       debian-ocaml-maint \
       debian-openoffice \
       debian-perl \
       debian-policy \
       debian-project \
       debian-python \
       debian-qa \
       debian-science"

# set -x
for list in $LISTS ; do
	rsync -a master.debian.org:/home/debian/lists/$list $CACHEDIR
done

rsync -a $CACHEDIR/* dbmed:$CACHEDIR
