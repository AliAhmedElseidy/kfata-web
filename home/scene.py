"""Selected public scene assets; never expose arbitrary document/private paths."""
import re
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods


def public_asset(asset):
    return bool(asset and not asset.collection.get_view_restrictions().exclude(restriction_type='none').exists())


def public_video(document):
    return bool(public_asset(document) and document.file_extension.lower() == 'mp4')


def validate_scene_settings(brand):
    errors = {}
    if brand.scene_enabled:
        for field in ['scene_video', 'scene_poster']:
            if not getattr(brand, field):
                errors[field] = 'اختر الملف قبل التفعيل / Select this asset before enabling.'
    for field in ['scene_video', 'scene_video_mobile']:
        doc = getattr(brand, field)
        if not doc:
            continue
        if not public_video(doc):
            errors[field] = 'اختر فيديو MP4 من مجموعة عامة / Choose an MP4 from a public collection.'
            continue
        try:
            with doc.file.open('rb') as file:
                signature = file.read(12)
            if signature[4:8] != b'ftyp' or doc.file.size > 6 * 1024 * 1024:
                errors[field] = 'Use a valid MP4 up to 6 MB, encoded as H.264 for browser playback.'
        except (OSError, ValueError):
            errors[field] = 'تعذر قراءة الملف / The selected file could not be read.'
    for field in ['scene_poster', 'scene_poster_mobile']:
        image = getattr(brand, field)
        if image and not public_asset(image):
            errors[field] = 'اختر صورة من مجموعة عامة / Choose an image from a public collection.'
    if errors:
        raise ValidationError(errors)


@require_http_methods(['GET', 'HEAD'])
def scene_video(request, document_id):
    from .models import BrandSettings
    brand = BrandSettings.load(request)
    if not brand.construction_scene_ready:
        raise Http404
    documents = [brand.scene_video, brand.scene_video_mobile]
    doc = next((d for d in documents if d and d.pk == document_id and public_video(d)), None)
    if not doc:
        raise Http404
    try:
        size = doc.file.size
    except (OSError, ValueError):
        raise Http404
    etag = '"' + doc.file_hash + '"' if doc.file_hash else None
    range_header = request.headers.get('Range')
    if request.headers.get('If-Range') and request.headers['If-Range'] != etag:
        range_header = None
    if not range_header and etag and request.headers.get('If-None-Match') == etag:
        response = HttpResponse(status=304)
    elif range_header:
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', range_header)
        start, end = 0, size - 1
        if match and any(match.groups()):
            first, last = match.groups()
            start = int(first) if first else max(0, size - int(last))
            end = min(int(last), size - 1) if first and last else size - 1
        if not match or not any(match.groups()) or start > end or start >= size or (not match[1] and match[2] == '0'):
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{size}'
            return response
        length = end - start + 1
        if request.method == 'HEAD':
            response = HttpResponse(content_type='video/mp4', status=206)
        else:
            def chunks():
                with doc.file.open('rb') as file:
                    file.seek(start)
                    remaining = length
                    while remaining:
                        data = file.read(min(65536, remaining))
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            response = StreamingHttpResponse(chunks(), content_type='video/mp4', status=206)
        response['Content-Length'] = length
        response['Content-Range'] = f'bytes {start}-{end}/{size}'
    elif request.method == 'HEAD':
        response = HttpResponse(content_type='video/mp4')
        response['Content-Length'] = size
    else:
        response = FileResponse(doc.file.open('rb'), content_type='video/mp4', filename=doc.filename)
    response['Accept-Ranges'] = 'bytes'
    response['Cache-Control'] = 'public, max-age=3600'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'"
    if etag:
        response['ETag'] = etag
    return response
