import fett
from docutils import statemachine
from docutils.utils.error_reporting import ErrorString
from docutils.parsers.rst import Directive


class SphinxGraphiQL(Directive):
    has_content: bool = False
    required_arguments: int = 0
    optional_arguments: int = 0
    final_argument_whitespace: bool = True
    option_spec = {"query": str, "response": str, "endpoint": str, "view_only": str}

    GRAPHIQL_TEMPLATE: str = '''
.. raw:: html

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/graphiql/3.8.0/graphiql.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.0.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.0.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/graphiql/3.8.0/graphiql.min.js"></script>
    <script src="https://unpkg.com/@graphiql/plugin-explorer/dist/index.umd.js" crossorigin></script>
    <link rel="stylesheet" href="https://unpkg.com/@graphiql/plugin-explorer/dist/style.css" />

    <div id="graphiql" style="height: 80vh; width:120vh; padding-left: 1vh"></div>

    <script>
        const graphQLFetcher = async (graphQLParams, options = {}) => {
            let headers = {};
            
            if (typeof options.headers === 'string') {
                try {
                    headers = JSON.parse(options.headers);
                } catch (e) {
                    console.log('Error parsing headers:', e);
                }
            } else if (options.headers) {
                headers = options.headers;
            }
            
            console.log("Headers being sent:", headers);
            
            return fetch('{{ endpoint }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: JSON.stringify(graphQLParams),
            }).then(response => response.json());
        };

        const explorerPlugin = GraphiQLPluginExplorer.explorerPlugin();
        
        ReactDOM.render(
            React.createElement(GraphiQL, {
                fetcher: graphQLFetcher,
                defaultEditorToolsVisibility: true,
                plugins: [explorerPlugin],
                defaultHeaders: JSON.stringify({
                    'Authorization': 'Bearer your-token-here'
                }, null, 2)
            }),
            document.getElementById('graphiql')
        );
    </script>
    '''

    def run(self):
        raw_template = fett.Template(self.GRAPHIQL_TEMPLATE)
        try:
            rendered_template = raw_template.render(self.options)
        except Exception as error:
            raise self.severe('Failed to render template: {}'.format(ErrorString(error)))

        rendered_lines = statemachine.string2lines(rendered_template, 4, convert_whitespace=1)

        self.state_machine.insert_input(rendered_lines, '')

        return []

