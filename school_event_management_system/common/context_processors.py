from os import environ


def school_context(request):
    return {'school': environ.get('SCHOOL_NAME')}
