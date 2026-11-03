"""Run on the Docker host. Never prints the generated credential or replaces an account."""
import json
from pathlib import Path
import secrets
import subprocess

directory = Path('/root/.config/kfata-web')
directory.mkdir(mode=0o700, parents=True, exist_ok=True)
directory.chmod(0o700)
credential = directory / 'owner-initial-password'
if credential.exists():
    raise SystemExit('Credential file already exists. No account changes made.')
password = secrets.token_urlsafe(30)
code = f'''from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(username='kfata-owner').exists():
    raise RuntimeError('Owner already exists; refusing to replace it')
User.objects.create_superuser(username='kfata-owner', email='', password={json.dumps(password)})
print('Owner account created; credential stays on the host.')
'''
with credential.open('x', encoding='utf-8') as output:
    credential.chmod(0o600)
    output.write(password + '\n')
subprocess.run(['docker','compose','exec','-T','web','python','manage.py','shell'], input=code, text=True, check=True)
print('Credential location: /root/.config/kfata-web/owner-initial-password')
