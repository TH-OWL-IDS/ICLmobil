# SPDX-FileCopyrightText: 2024 iplus1 GmbH <info@iplus1.de>
# SPDX-License-Identifier: AGPL-3.0-only

pyphoton:

https://github.com/astagi/pyphoton/tree/7bc71c5bd86c0d70580c71ea6945b44d11bd6b1d

Patch:

```diff
diff --git a/requirements.txt b/requirements.txt
index a8ed785..ee88e26 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1 @@
-requests==2.26.0
+requests>=2.26.0
diff --git a/setup.py b/setup.py
index 88d07a0..13ffc61 100644
--- a/setup.py
+++ b/setup.py
@@ -4,7 +4,7 @@ setup(
     name='pyphoton',
     version='1.0.0',
     url='https://github.com/astagi/pyphoton',
-    install_requires=["requests==2.26.0"],
+    install_requires=["requests>=2.26.0"],
     description="Photon Python client",
     long_description=open('README.rst', 'r').read(),
     license="MIT",
```
