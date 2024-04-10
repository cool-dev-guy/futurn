# pyturner
A cool turnstile bypass.

This is a modified,async and api version of a turnstile bypass algorithm,written in a way that it will give results in `2 to 3` seconds.

## Usage
```
POST https://the-domain-of-deployment.com/turnstile/SITE_ID
data = {
    "url":"https://site-that-has-turnstile.com",
    "invisible":true
}
```

## How to deploy ?
I have added a dockerfile so just clone and deploy it.

## Thanks
- [Turnstile Solver Algorithm](https://github.com/Body-Alhoha/turnaround/)
