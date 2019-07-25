#!/bin/bash
set -ev

if [[ -z $TRAVIS_TAG ]]; then
  echo TRAVIS_TAG unset, exiting
  exit 1
fi

BUILD_REPO_URL=https://github.com/terracoin/electrum-trc.git

cd build

git clone --branch $TRAVIS_TAG $BUILD_REPO_URL electrum-trc

cd electrum-trc

export PY36BINDIR=/Library/Frameworks/Python.framework/Versions/3.6/bin/
export PATH=$PATH:$PY36BINDIR
source ./contrib/terracoin/travis/electrum_trc_version_env.sh;
echo osx build version is $TERRACOIN_ELECTRUM_VERSION


git submodule init
git submodule update

info "Building CalinsQRReader..."
d=contrib/CalinsQRReader
pushd $d
rm -fr build
xcodebuild || fail "Could not build CalinsQRReader"
popd

sudo pip3 install --no-warn-script-location -r contrib/deterministic-build/requirements.txt
sudo pip3 install --no-warn-script-location -r contrib/deterministic-build/requirements-hw.txt
sudo pip3 install --no-warn-script-location -r contrib/deterministic-build/requirements-binaries.txt
sudo pip3 install --no-warn-script-location PyInstaller==3.4 --no-use-pep517

export PATH="/usr/local/opt/gettext/bin:$PATH"
./contrib/make_locale
find . -name '*.po' -delete
find . -name '*.pot' -delete

cp contrib/terracoin/osx.spec .
cp contrib/terracoin/pyi_runtimehook.py .
cp contrib/terracoin/pyi_tctl_runtimehook.py .

pyinstaller \
    -y \
    --name electrum-trc-$TERRACOIN_ELECTRUM_VERSION.bin \
    osx.spec

info "Adding Terracoin URI types to Info.plist"
plutil -insert 'CFBundleURLTypes' \
   -xml '<array><dict> <key>CFBundleURLName</key> <string>terracoin</string> <key>CFBundleURLSchemes</key> <array><string>terracoin</string></array> </dict></array>' \
   -- dist/Terracoin\ Electrum.app/Contents/Info.plist \
   || fail "Could not add keys to Info.plist. Make sure the program 'plutil' exists and is installed."

sudo hdiutil create -fs HFS+ -volname "Terracoin Electrum" \
    -srcfolder dist/Terracoin\ Electrum.app \
    dist/Terracoin-Electrum-$TERRACOIN_ELECTRUM_VERSION-macosx.dmg
