from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('thingsapp', 'templates'))
def render_template(name, **vars):
    return env.get_template(name).render(**vars)
