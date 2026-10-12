# Security policy

## Supported versions

Security fixes are made for the latest release only. The Windows installer, the macOS app and the Linux AppImage
update themselves; the `.deb` package must be reinstalled from the [latest release](https://github.com/utkarsh-1912/geocore/releases/latest).

| Version | Supported |
| :--- | :--- |
| Latest release | Yes |
| Older releases | No; please update |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report it privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**.
Include:

- the GeoCore version and operating system;
- what an attacker could do, and how (steps, a proof of concept or a sample file);
- any suggested fix.

You can expect an acknowledgement within a week. Once the issue is confirmed, a fix is prepared and released, and
the report is credited in the changelog unless you prefer otherwise.

## Scope

GeoCore runs locally:

- the backend listens on `127.0.0.1:8000` only;
- GeoAI loads models from the local disk;
- GeoAI can call only the validated tools in its registry, never arbitrary code, shell, SQL or file operations.

Reports of special interest:

- anything that lets a project file (AGS, CSV, Excel, saved objects) or a document indexed for GeoAI execute code
  or read files outside its scope;
- ways for model output to bypass the tool registry's validation;
- network access the documentation does not describe (GeoCore should contact only GitHub Releases for updates,
  and model download sources when you start a download);
- problems in the installers or the update mechanism.

Incorrect engineering results are bugs, not security issues. Please report them with the bug report form.
