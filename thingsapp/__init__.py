import logging

from appscript import *

from thingsapp.util import render_template

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class Things(object):
    """Represent a running Things application"""

    def __init__(self):
        self.t = app('Things')
        
        # map ID of a to_do to the properties dictionary
        self.to_dos = {}
        self.projects = {}
        self.areas = {}

        # map ID of a to_do to the ID of a project/area
        self._projectmap = {}
        self._areamap = {}

        self._load()

    def _load(self):
        """Load all todos, projects and areas from Things applescript"""
        LOG.debug('loading to_dos')
        for props in self.t.to_dos.properties():
            self.to_dos[props[k.id]] = o = AppleScriptObject.create(self, props)
            if isinstance(o, Project):
                self.projects[props[k.id]] = o
            
        LOG.debug('loading areas')
        for props in self.t.areas.properties():
            self.areas[props[k.id]] = AppleScriptObject.create(self, props)

        LOG.debug('assigning projects (might take some time)')
        for obj in self.to_dos.values():
            prj = obj._props[k.project]
            if prj != k.missing_value:
                self._projectmap[obj.id] = prj.id()

        LOG.debug('assigning areas (might take some time)')
        for obj in self.to_dos.values():
            area = obj._props[k.area]
            if area != k.missing_value:
                self._areamap[obj.id] = area.id()

        LOG.debug('loading focus lists')
        self.inbox = FocusList(self, 'inbox')
        self.logbook = FocusList(self, 'logbook')

class AppleScriptObject(object):

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

    @property
    def project(self):
        project = self._props[k.project]
        if project != k.missing_value:
            project_id = self._things._projectmap[self.id]
            project = self._things.to_dos[project_id]
        return project

    @property
    def area(self):
        area = self._props[k.area]
        if area != k.missing_value:
            area_id = self._things._areamap[self.id]
            area = self._things.areas[area_id]
        return area

class Project(ToDo):

    @property
    def to_dos(self):
        return [o for o in self._things.to_dos.values()
                if not isinstance(o, Project)]

class Area(AppleScriptObject):

    pass

class FocusList(tuple):

    def __new__(cls, things, focusname):
        return super(FocusList, cls).__new__(
            cls,
            tuple(cls._load(things, focusname)))

    @classmethod
    def _load(cls, things, focusname):
        props_list = things.t.lists[focusname].to_dos.properties()
        return [things.to_dos[props[k.id]]
                for props in props_list]


def dump_todos():
    things = Things()
    
    LOG.info('writing logbook')
    with open('tmp/logbook.html', 'w') as f:
        f.write(render_template(
                'list.html',
                title='LogBook',
                to_dos=things.logbook,
                k=k))

    for project in things.projects.values():
        pathname = project.name.replace('/', '-')
        LOG.info('writing project %s', project.name)
        with open('tmp/project-{0}.html'.format(pathname), 'w') as f:
            f.write(render_template(
                    'list.html',
                    title='Project: {0}'.format(project.name),
                    to_dos=project.to_dos,
                    k=k))

play = dump_todos
