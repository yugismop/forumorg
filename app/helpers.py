import os

from werkzeug import secure_filename

from app import s3_client


def get_resume_url(oid, full_name):
    filename = secure_filename(f'CV_{full_name}')
    cdr = f'inline; filename={filename}.pdf'
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'ResponseContentDisposition': cdr, 'Bucket': os.environ.get('BUCKET_NAME'), 'Key': f'resumes/{oid}.pdf'}
    )
    return url
