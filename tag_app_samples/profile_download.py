import subprocess
import sys

profile_package_name = "none-existing-profile"

process = subprocess.check_output(
    [sys.executable,
     "-m", "pip",
     "install", "--upgrade",
     "--trusted-host", "tagubuntu.network.com",
     "--index-url", f"http://tagubuntu.network.com:8081/tag/dev_wen",
     "--extra-index-url", "http://pypi.org/simple", profile_package_name,
     ]  # type: ignore
)


process = process.decode()
for line in iter(process.split('\n')):
    print(line)