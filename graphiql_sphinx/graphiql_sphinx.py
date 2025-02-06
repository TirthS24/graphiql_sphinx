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

    <div id="graphiql" style="height: 80vh; width:45vw; padding-left: 1vh; margin-top:40px"></div>

    <script>
        // Function to get the authentication token from the auth template
        async function getAuthToken() {
            try {
                // This assumes your auth.html template sets up a function called getAuthenticationToken
                // that returns a Promise resolving to the token
                if (typeof window.getAuthenticationToken === 'function') {
                    const token = await window.getAuthenticationToken();
                    return token;
                }
                return null;
            } catch (error) {
                console.error('Error getting authentication token:', error);
                return null;
            }
        }

        // Create a fetcher that automatically handles authentication
        const graphQLFetcher = async (graphQLParams, options = {}) => {
            // Get authentication token
            const authObj = await getAuthToken();
            const authToken = authObj ? authObj.token : null;
            const authType = authObj ? authObj.token_type : null;
            
            let headers = {
                'Content-Type': 'application/json',
            };

            // Add authentication header if token is available
            if (authToken) {
                if (authType == 'COGNITO_JWT') 
                    headers['Authorization'] = authToken;
                else if (authType == 'API_KEY')
                    headers['x-api-key'] = authToken;
            }

            // Merge with any user-provided headers
            if (options.headers) {
                try {
                    const userHeaders = typeof options.headers === 'string' 
                        ? JSON.parse(options.headers)
                        : options.headers;
                    headers = { ...headers, ...userHeaders };
                } catch (e) {
                    console.error('Error parsing headers:', e);
                }
            }

            try {
                const response = await fetch('{{ endpoint }}', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(graphQLParams),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('GraphQL request error:', error);
                throw error;
            }
        };

        // Set up GraphiQL with the explorer plugin
        const explorerPlugin = GraphiQLPluginExplorer.explorerPlugin();

        // Function to initialize GraphiQL
        async function initializeGraphiQL() {
            const authToken = await getAuthToken();
            const defaultHeaders = authToken ? 
                JSON.stringify({ 'Authorization': authToken }, null, 2) : 
                '{}';

            ReactDOM.render(
                React.createElement(GraphiQL, {
                    fetcher: graphQLFetcher,
                    defaultEditorToolsVisibility: true,
                    plugins: [explorerPlugin],
                    defaultHeaders: defaultHeaders,
                    shouldPersistHeaders: true
                }),
                document.getElementById('graphiql')
            );
        }

        // Initialize GraphiQL once the page loads
        window.addEventListener('load', initializeGraphiQL);
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

