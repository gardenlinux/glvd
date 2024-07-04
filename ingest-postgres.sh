#!/bin/bash

set -euo pipefail

mkdir -p data/ingest-debsec/{debian,gardenlinux}/CVE
mkdir -p data/ingest-debsec/debian/CVE
mkdir -p data/ingest-debsrc/debian
mkdir -p data/ingest-debsrc/var/lib/dpkg
touch data/ingest-debsrc/var/lib/dpkg/status
curl https://salsa.debian.org/security-tracker-team/security-tracker/-/raw/master/data/CVE/list?ref_type=heads \
    --output data/ingest-debsec/debian/CVE/list
mkdir -p conf/ingest-debsrc/
curl https://raw.githubusercontent.com/gardenlinux/glvd-data-ingestion/main/conf/ingest-debsrc/apt.conf \
    --output conf/ingest-debsrc/apt.conf
curl https://raw.githubusercontent.com/gardenlinux/glvd-data-ingestion/main/conf/ingest-debsrc/debian.sources \
    --output conf/ingest-debsrc/debian.sources
APT_CONFIG=conf/ingest-debsrc/apt.conf apt-get -q update \
-o Dir="$PWD/data/ingest-debsrc/" \
-o Dir::Etc::sourcelist="$PWD/conf/ingest-debsrc/debian.sources" \
-o Dir::State="$PWD/data/ingest-debsrc/"
git clone --depth=1 https://salsa.debian.org/security-tracker-team/security-tracker

mkdir -p gardenlinux-packages
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.0/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.0.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.1/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.1.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.2/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.2.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.3/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.3.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.5/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.5.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.7/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.7.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.8/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.8.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/1443.9/main/binary-amd64/Packages.gz > gardenlinux-packages/1443.9.gz
curl -s https://packages.gardenlinux.io/gardenlinux/dists/today/main/binary-amd64/Packages.gz > gardenlinux-packages/today.gz
gunzip gardenlinux-packages/1443*.gz
gunzip gardenlinux-packages/today.gz

echo "Run data ingestion (ingest-debsrc - debian trixie)"
glvd-data ingest-debsrc debian trixie data/ingest-debsrc/lists/deb.debian.org_debian_dists_trixie_main_source_Sources
echo "Run data ingestion (ingest-debsrc - debian bookworm)"
glvd-data ingest-debsrc debian bookworm data/ingest-debsrc/lists/deb.debian.org_debian_dists_bookworm_main_source_Sources
echo "Run data ingestion (ingest-debsec - debian)"
glvd-data ingest-debsec debian security-tracker/data
echo "Run data ingestion (ingest-debsrc - gardenlinux today)"
glvd-data ingest-debsrc gardenlinux today ./gardenlinux-packages/today
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.0)"
glvd-data ingest-debsrc gardenlinux 1443.0 ./gardenlinux-packages/1443.0
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.1)"
glvd-data ingest-debsrc gardenlinux 1443.1 ./gardenlinux-packages/1443.1
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.2)"
glvd-data ingest-debsrc gardenlinux 1443.2 ./gardenlinux-packages/1443.2
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.3)"
glvd-data ingest-debsrc gardenlinux 1443.3 ./gardenlinux-packages/1443.3
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.5)"
glvd-data ingest-debsrc gardenlinux 1443.5 ./gardenlinux-packages/1443.5
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.7)"
glvd-data ingest-debsrc gardenlinux 1443.7 ./gardenlinux-packages/1443.7
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.8)"
glvd-data ingest-debsrc gardenlinux 1443.8 ./gardenlinux-packages/1443.8
echo "Run data ingestion (ingest-debsrc - gardenlinux 1443.9)"
glvd-data ingest-debsrc gardenlinux 1443 ./gardenlinux-packages/1443.9
echo "Run data ingestion (nvd)"
glvd-data ingest-nvd
echo "Run data combination (combine-deb)"
glvd-data combine-deb
echo "Run data combination (combine-all)"
glvd-data combine-all
