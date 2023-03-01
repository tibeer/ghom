# Release

## How to create a release

This is mainly for @tibeer to create a new release of this action.

1. Tag the container with a new version:

   Always create a new tag for all three possible tags: `major`, `major.minor`, `major.minor.patch`

   ```sh
   # define new tag
   export MAJOR=1
   export MINOR=51
   export PATCH=3
   # get latest image
   podman pull "ghcr.io/tibeer/ghom:latest"
   # push new tags
   podman push "ghcr.io/tibeer/ghom:latest" "ghcr.io/tibeer/ghom:${MAJOR}"
   podman push "ghcr.io/tibeer/ghom:latest" "ghcr.io/tibeer/ghom:${MAJOR}.${MINOR}"
   podman push "ghcr.io/tibeer/ghom:latest" "ghcr.io/tibeer/ghom:${MAJOR}.${MINOR}.${PATCH}"
   # also remove latest image
   podman image rm "ghcr.io/tibeer/ghom:latest"
   ```

2. Change the `action.yml` file container tag to the most detailed version: `major.minor.patch`
3. Tag the repository with a new version

   ```sh
   # define new tag
   export MAJOR=1
   export MINOR=51
   export PATCH=3
   # tag current state
   git tag "${MAJOR}" main
   git tag "${MAJOR}.${MINOR}" main
   git tag "${MAJOR}.${MINOR}.${PATCH}" main
   # push tags
   git push origin "${MAJOR}"
   git push origin "${MAJOR}.${MINOR}"
   git push origin "${MAJOR}.${MINOR}.${PATCH}"
   ```

4. Create a new release: <https://github.com/tibeer/ghom/releases/new>

## Release pattern

We'll use [semver](https://semver.org/) vor versioning (and we'll not use a stupid "v" prefix).

1. Major: Something drastically changes (e.g. PyGithub is replaced by something else, ghom config file is not backwards compatible)
2. Minor: Functionality is added
3. Patch: Bug fixes

Testing will always be done on the "latest" tag.
