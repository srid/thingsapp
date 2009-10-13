import logging

from thingsapp.util import render_template

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def play():
    from appscript import app, k
    logbook = app('Things').lists['LogBook'].to_dos()
    LOG.debug('retrieved Things data')

    print render_template(
        'list.html',
        to_dos=logbook,
        k=k)

