from .dev import *
STORAGES['staticfiles'] = {'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}
