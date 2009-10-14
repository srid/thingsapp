import logging

from appscript import *

from thingsapp.util import render_template

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class Things(object):
    """Represent a running Things application

    Initialling the ``Things`` objects will pull *all* data from the running
    Things.app as faster as possible. It should take about 4 seconds.

    >>> things = Things()

    Then you can access the to dos, projects and areas are simple lists.

    >>> things.to_dos
    >>> things.projects
    >>> things.areas

    Each item of the list is a simple Python object representing the underlying
    Things data, for instance::

    >>> things.to_dos[0].name
    'Submit the final proposal'
    >>> things.to_dos[0].project.name
    'PyCon 2010'

    You can also access the focus lists in Things::

    >>> things.inbox
    >>> things.logbook
    >>> ...
    """

    def __init__(self):
        self.t = app('Things')
        
        # map ID of a to_do/area to the wrapper object
        self._to_dos = {}
        self._areas = {}

        # map ID of a to_do to the ID of a project/area
        self._projectmap = {}
        self._areamap = {}

        self.to_dos = []
        self.projects = []
        self.areas = []

        self._load()

    def _load(self):
        """Load all todos, projects and areas from Things applescript"""
        LOG.debug('loading to_dos')
        for props in self.t.to_dos.properties():
            self._to_dos[props[k.id]] = o = AppleScriptObject.create(self, props)
            self.to_dos.append(o)
            if isinstance(o, Project):
                self.projects.append(o)
            
        LOG.debug('loading areas')
        for props in self.t.areas.properties():
            self._areas[props[k.id]] = o = AppleScriptObject.create(self, props)
            self.areas.append(o)

        LOG.debug('assigning projects (might take some time)')
        for obj in self.to_dos:
            prj = obj._props[k.project]
            if prj != k.missing_value:
                self._projectmap[obj.id] = prj.id()

        LOG.debug('assigning areas (might take some time)')
        for obj in self.to_dos:
            area = obj._props[k.area]
            if area != k.missing_value:
                self._areamap[obj.id] = area.id()

        LOG.debug('loading focus lists')
        self.inbox = FocusList(self, 'inbox')
        self.today = FocusList(self, 'today')
        self.next = FocusList(self, 'next')
        self.scheduled = FocusList(self, 'scheduled')
        self.someday = FocusList(self, 'someday')
        self.logbook = FocusList(self, 'logbook')

class AppleScriptObject(object):
    """A wrapper around appscript's Reference

    This wrapper enables one to access the properties of the Referenced object
    using Pythonic dotted reference.
    """

    @classmethod
    def create(cls, things, props):
        """Create an object from the appropriate subclass"""
        class_ = props[k.class_]
        if class_ == k.project:
            return Project(things, props)
        elif class_ == k.selected_to_do:
            return ToDo(things, props)
        elif class_ == k.area:
            return Area(things, props)
        else:
            raise NotImplementedError, 'unsupported class: %s' % class_

    def __init__(self, things, props):
        self._props = props
        self._things = things

    def __getattr__(self, name):
        name = getattr(k, name)
        if name in self._props:
            return self._props[name]
        else:
            raise AttributeError, 'Property "%s" missing in props: %s' % (
                name, self._props)

class ToDo(AppleScriptObject):
    """Represents a to do object in Things.

    Note that projects are also a to do object
    """

    @property
    def project(self):
        project = self._props[k.project]
        if project != k.missing_value:
            project_id = self._things._projectmap[self.id]
            project = self._things._to_dos[project_id]
        return project

    @property
    def area(self):
        area = self._props[k.area]
        if area != k.missing_value:
            area_id = self._things._areamap[self.id]
            area = self._things._areas[area_id]
        return area

class Project(ToDo):
    """Represents a project object in Things.

    Projects are to dos with sub to dos in them
    """

    @property
    def to_dos(self):
        return [o for o in self._things.to_dos
                if not isinstance(o, Project)]

class Area(AppleScriptObject):
    """Represents an area in Things."""


class FocusList(tuple):
    """Represent the various focus lists in Things

    Examples: Inbox, Next, LogBook, etc...
    """

    def __new__(cls, things, focusname):
        return super(FocusList, cls).__new__(
            cls,
            tuple(cls._load(things, focusname)))

    @classmethod
    def _load(cls, things, focusname):
        props_list = things.t.lists[focusname].to_dos.properties()
        return [things._to_dos[props[k.id]]
                for props in props_list]


def play():
    things = Things()
    
    LOG.info('writing logbook')
    with open('tmp/logbook.html', 'w') as f:
        f.write(render_template(
                'list.html',
                title='LogBook',
                to_dos=things.logbook,
                k=k))

    for project in things.projects:
        pathname = project.name.replace('/', '-')
        LOG.info('writing project %s', project.name)
        with open('tmp/project-{0}.html'.format(pathname), 'w') as f:
            f.write(render_template(
                    'list.html',
                    title='Project: {0}'.format(project.name),
                    to_dos=project.to_dos,
                    k=k))
