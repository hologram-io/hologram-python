#!/bin/bash
set -euo pipefail

# Change these values!!!
PYTHON_SDK_GITHUB_DIR='../../GithubRepos/hologram-python'
HOLOGRAM_DOCS_RELEASE_BRANCH='T2883'
HOLOGRAM_DOCS_DIR='../hologram-docs'
VERSION_NUMBER='0.5.0'

SDK_VERSION="v$VERSION_NUMBER"

function pause() {
  read -p "$*"
}

echo '-----------------------------------'
echo 'STAGE 1: MERGING DEVELOP ONTO MASTER IN PHABRICATOR REPO'
echo '-----------------------------------'

echo 'Merging master onto develop'
pause 'Press [Enter] key to continue...'
git checkout develop
git pull
git merge master
echo 'Merging master onto develop successful!'

echo 'Checking out master and merging develop onto it'
pause 'Press [Enter] key to continue...'
git checkout master
git pull
git merge develop
echo 'Adding SDK release tag and pushing it back to Phabricator'
pause 'Press [Enter] key to continue...'
git tag -a "${SDK_VERSION:?}" -m "Hologram Python SDK ${SDK_VERSION:?} release"
git push
git push --tags
echo 'Push successful!'


echo '-----------------------------------'
echo 'STAGE 2: GITHUB SYNC'
echo '-----------------------------------'

echo 'Syncing with hologram-python (GitHub repo)'
pause 'Press [Enter] key to continue...'
rsync -a --exclude-from=.gitignore --exclude=.git/ --exclude=change-version-number.sh --exclude=sync-to-github.sh --exclude=.arcconfig . "${PYTHON_SDK_GITHUB_DIR:?}" --delete
echo 'Sync successful'

echo 'Changing to GitHub repo...'
pause 'Press [Enter] key to continue...'
cd "${PYTHON_SDK_GITHUB_DIR:?}" || exit
echo 'Now in GitHub repo...'

echo 'Removing TOTP and HOTP source files'
pause 'Press [Enter] key to continue...'
rm Hologram/Authentication/HOTPAuthentication.py
rm Hologram/Authentication/TOTPAuthentication.py
echo 'Removed both files successfully'

echo "Committing and tagging hologram-python for ${SDK_VERSION:?} release"
pause 'Press [Enter] key to continue...'
git add .
git commit -m "Hologram Python SDK ${SDK_VERSION:?} release"
git tag -a "${SDK_VERSION:?}" -m "Hologram Python SDK ${SDK_VERSION:?} release"
echo 'Committed and tagged hologram-python sdk for release'

echo 'Pushing to Hologram GitHub Repo'
pause 'Press [Enter] key to continue...'
git push
git push --tags
echo 'Pushed to GitHub successfully'



echo '-----------------------------------'
echo 'STAGE 3: BUILDING AND UPLOADING PYPI PACKAGE'
echo '-----------------------------------'

echo 'Remove dist and egg-info folders'
rm -rf dist
rm -rf hologram_python.egg-info
echo 'Removed them successfully!'


echo 'Building PyPI sdist package'
python setup.py sdist
echo 'PyPI sdist package built successfully'


echo 'Uploading to PyPI'
pause 'Press [Enter] key to continue...'
twine upload dist/*
echo 'Upload successful!'

cd -

echo '-----------------------------------'
echo 'STAGE 4: Updating Hologram Docs'
echo '-----------------------------------'

echo 'Changing to hologram-docs repo...'
pause 'Press [Enter] key to continue...'
cd "${HOLOGRAM_DOCS_DIR:?}" || exit
echo 'Now in hologram-docs repo...'

echo "Merge ${HOLOGRAM_DOCS_RELEASE_BRANCH:?} onto develop..."
pause 'Press [Enter] key to continue...'
git checkout develop
git pull
git checkout "${HOLOGRAM_DOCS_RELEASE_BRANCH:?}"
arc land
echo 'Landed docs release successfully!'
