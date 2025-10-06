# ICLMobil Backend

For documentation, see [Documentation overview](deployment/containers/documentation/docs/index.md).

## Licenses used

The main license used for software written as part of the project as well as documentation and other assets is
[GNU Affero General Public License version 3.0 (only)](https://spdx.org/licenses/AGPL-3.0-only.html#licenseText).

Other licenses used (f.e. for fragments of other authors who released it as such) are noted in the corresponding
file headers or in `.reuse/dep5`.

Licenses actually used are gathered using the check described below in the
[License check for all sources in this repository](#license-check-for-all-sources-in-this-repository).
The current list of licenses used is:

- 0BSD,
- AGPL-3.0-only
- BSD-3-Clause
- MIT
- PostgreSQL

For the full text of the licenses, please refer to the [`LICENSES/`](LICENSES/) subdirectory.

## License check for all sources in this repository

All files must be annotated with [SPDX](https://spdx.dev/learn/handling-license-info/)-compatible headers.
If that is not possible (e.g. for binary or vendored files), see [](.reuse/dep5)
for a way to annotate those.

All licenses must be put into [`LICENSES/`](LICENSES/) and be references by their filename.

Before each release, check if these requirements are met.
Using Docker, this can be done like this:

```bash
docker run --rm -i -v "$(pwd):/data:ro" fsfe/reuse:3.0 --suppress-deprecation lint && echo SUCCESS
```

If `SUCCESS` is printed, the check was OK. Otherwise, consult the output for hints.
