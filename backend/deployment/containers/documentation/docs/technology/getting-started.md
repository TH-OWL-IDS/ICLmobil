# Getting started

## Deployment

Requirements:

- x86 Server with 4 CPU cores, 16 GiB RAM, 64 GiB Storage or more
- Tools expected in operating system
  - `docker` with compose plugin
  - `bash`
  - `column` (Debian package `bsdmainutils`)
  - `jq` (Debian package `jq`)

1. Clone this repository into e.g. a directory called `backend`.
2. To build the container images, run

    ```bash
    user@iclmobil-dev1:~/iclmobil$ cd backend/deployment/
    user@iclmobil-dev1:~/iclmobil/backend/deployment$ manage/build.sh
    ```

3. Create a copy of `env.sample` as `.env`.
4. Go through `.env` and configure everything according to the comments there.
5. To start the containers, run:

    ```bash
    user@iclmobil-dev1:~/iclmobil/backend/deployment$ manage/start.sh
    ```

The backend should now be available. For relevant URLs, see [Relevant URLs available after deployment](../urls.md).
