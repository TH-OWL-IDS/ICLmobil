# Relevant URLs available after deployment

Backend components are reachable under the following URLs: 

- Internal (but publicly visible), interactive API documentation:
  https://PUBLIC_URL/api/v1/docs/
- Low-level administration web UI (only reachable after login as administrative user)
  https://PUBLIC_URL/admin-backend/
- This documentation (only reachable after login as administrative user)
  https://PUBLIC_URL/documentation/

`PUBLIC_URL` is the URL configured under that key in `.env`.

The root URL (e.g. https://PUBLIC_URL/) will be redirected to the URL configured under `ROOT_REDIRECT_URL` in `.env`.