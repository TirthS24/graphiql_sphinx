from .graphiql_sphinx import SphinxGraphiQL

def setup(app):
    app.add_directive('graphiql', SphinxGraphiQL)

    return {'parallel_read_safe': True,
            'parallel_write_safe': True}
