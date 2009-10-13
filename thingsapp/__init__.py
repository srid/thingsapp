import logging

from thingsapp.util import render_template

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def play():
    from appscript import app, k
    Things = app('Things')
    LOG.debug('initialized things applescript bridge')
    
    LOG.info('writing logbook')
    with open('tmp/logbook.html', 'w') as f:
        logbook = Things.lists['LogBook'].to_dos()
        f.write(render_template(
                'list.html',
                title='LogBook',
                to_dos=logbook,
                k=k))

    for project in Things.projects():
        name = project.name()
        pathname = name.replace('/', '-')
        LOG.info('writing project %s', name)
        with open('tmp/project-{0}.html'.format(pathname), 'w') as f:
            f.write(render_template(
                    'list.html',
                    title='Project: {0}'.format(name),
                    to_dos=project.to_dos(),
                    k=k))
