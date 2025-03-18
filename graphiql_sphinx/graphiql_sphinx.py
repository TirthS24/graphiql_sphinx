import fett
from docutils import statemachine
from docutils.utils.error_reporting import ErrorString
from docutils.parsers.rst import Directive


class SphinxGraphiQL(Directive):
    has_content: bool = False
    required_arguments: int = 0
    optional_arguments: int = 0
    final_argument_whitespace: bool = True
    option_spec = {"query": str, "response": str, "graphql_endpoint": str, "view_only": str, "auth_endpoint": str}

    GRAPHIQL_TEMPLATE: str = '''
.. raw:: html

    <!-- CSS Dependencies -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/graphiql/3.8.0/graphiql.min.css">
    <link rel="stylesheet" href="https://unpkg.com/@graphiql/plugin-explorer/dist/style.css" />
    
    <!-- JavaScript Dependencies -->
    <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/graphiql/3.8.0/graphiql.min.js"></script>
    <script crossorigin src="https://unpkg.com/@graphiql/plugin-explorer/dist/index.umd.js"></script>
    <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>

    <!-- <style>
        /* Reset styles for GraphiQL container */
        .graphiql-container {
            height: 600px !important;
        }
        
        /* Reset styles for form container */
        .container1 {
            width: 100% !important;
            max-width: none !important;
            padding: 0px;
            border-radius: 8px;
            # box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            # margin-bottom: 20px;
            # margin-left:56px;
            # margin-right:56px;
        }
        
        /* Override any max-width constraints from the theme */
        #root, #graphiql {
            max-width: none !important;
        }
        
        /* Add specific fixes for the SphinxAwesome theme */
        .sphinx-container .main-content .body .section > .container1,
        .sphinx-container .main-content .body .section > #root,
        .sphinx-container .main-content .body .section > #graphiql {
            max-width: none !important;
            width: 100% !important;
            padding: 0;
        }
        
        /* Form styling */
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        select, input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            color: #000;
        }
        .error {
            color: #c62828;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .response {
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .hidden {
            display: none !important;
        }
        
        /* Ensure GraphiQL is visible at full width */
        #graphiql {
            position: relative;
            width: 75vw !important;
            height: 600px !important;
            margin-top: 20px;
            overflow: hidden;
        }
        
        /* Fix for the GraphiQL Explorer plugin */
        .graphiql-explorer-root {
            width: auto !important;
        }
        
        /* Ensure full width for the container */
        .graphiql-container,
        .graphiql-container .editorWrap,
        .graphiql-container .queryWrap,
        .graphiql-container .resultWrap {
            flex: 1 1 auto !important;
            width: 100% !important;
        }
    </style> -->
    
    <div class="sphinx-graphiql-wrapper">
        <div id="root"></div>
        <div id="graphiql" class="hidden" style="height: 100vh;"></div>
    </div>

    <script type="text/babel">
        // Global variables to store authentication details
        let GLOBAL_AUTH_TOKEN = null;
        let GLOBAL_API_KEY = null;
        let GLOBAL_TOKEN_TYPE = null;

        const AuthTokenForm = () => {
            const [authType, setAuthType] = React.useState('COGNITO');
            const [formData, setFormData] = React.useState({});
            const [response, setResponse] = React.useState(null);
            const [error, setError] = React.useState(null);
            const [isGraphiQLInitialized, setIsGraphiQLInitialized] = React.useState(false);

            React.useEffect(() => {
                const graphiqlElement = document.getElementById('graphiql');
                if (response && !isGraphiQLInitialized) {
                    graphiqlElement.classList.remove('hidden');
                    initializeGraphiQL();
                    setIsGraphiQLInitialized(true);
                } else if (!response) {
                    graphiqlElement.classList.add('hidden');
                    if (isGraphiQLInitialized) {
                        ReactDOM.unmountComponentAtNode(document.getElementById('graphiql'));
                        setIsGraphiQLInitialized(false);
                    }
                }
            }, [response, isGraphiQLInitialized]);

            const handleInputChange = (e) => {
                setFormData({
                    ...formData,
                    [e.target.name]: e.target.value
                });
            };

            const handleSubmit = async (e) => {
                e.preventDefault();
                setError(null);
                setResponse(null);

                try {
                    const payload = {
                        auth_type: authType,
                        ...formData
                    };

                    const response = await fetch('{{auth_endpoint}}', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(payload),
                    });

                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'Failed to get token');
                    }

                    GLOBAL_AUTH_TOKEN = data.authorization_header;
                    GLOBAL_TOKEN_TYPE = data.token_type;
                    
                    // Handle API key from additional_headers if present
                    if (data.additional_headers && data.additional_headers['x-api-key']) {
                        GLOBAL_API_KEY = data.additional_headers['x-api-key'];
                    } else {
                        GLOBAL_API_KEY = null;
                    }

                    setResponse(data);
                } catch (err) {
                    setError(err.message);
                    GLOBAL_AUTH_TOKEN = null;
                    GLOBAL_API_KEY = null;
                    GLOBAL_TOKEN_TYPE = null;
                }
            };

            const handleLogout = () => {
                GLOBAL_AUTH_TOKEN = null;
                GLOBAL_API_KEY = null;
                GLOBAL_TOKEN_TYPE = null;
                setResponse(null);
                setFormData({});
                setError(null);
            };

            const authFields = {
                COGNITO: ['username', 'password', 'client_id', 'user_pool_id', 'region'],
                API_KEY: ['api_key'],
                BOTH: ['username', 'password', 'client_id', 'user_pool_id', 'region', 'api_key']
            };

            return (
                React.createElement('div', { className: 'container1' },
                    React.createElement('h2', null, 'Get Authorization Token'),
                    !response ? (
                        React.createElement('form', { onSubmit: handleSubmit },
                            React.createElement('div', { className: 'form-group' },
                                React.createElement('label', null, 'Authentication Type'),
                                React.createElement('select', {
                                    value: authType,
                                    onChange: (e) => {
                                        setAuthType(e.target.value);
                                        setFormData({});
                                    }
                                },
                                    Object.keys(authFields).map(type => 
                                        React.createElement('option', { key: type, value: type }, type)
                                    )
                                )
                            ),
                            authFields[authType].map(field => 
                                React.createElement('div', { key: field, className: 'form-group' },
                                    React.createElement('label', null, 
                                        field.split('_').map(word => 
                                            word.charAt(0).toUpperCase() + word.slice(1)
                                        ).join(' ')
                                    ),
                                    React.createElement('input', {
                                        type: field.includes('password') ? 'password' : 'text',
                                        name: field,
                                        value: formData[field] || '',
                                        onChange: handleInputChange,
                                        required: true
                                    })
                                )
                            ),
                            React.createElement('button', { type: 'submit', id: 'token-btn' }, 'Login')
                        )
                    ) : (
                        React.createElement('div', null,
                            React.createElement('div', { className: 'response' },
                                React.createElement('h3', null, 'Authentication Status: Active'),
                                React.createElement('p', null, 'You can now use the GraphiQL explorer below.'),
                                React.createElement('br', null),
                                React.createElement('p', null, 'Please click the Re-fetch button to Execute Queries.')
                            ),
                            React.createElement('button', { onClick: handleLogout }, 'Logout')
                        )
                    ),
                    error && (
                        React.createElement('div', { className: 'error' }, error)
                    )
                )
            );
        };

        const graphQLFetcher = async (graphQLParams, options = {}) => {
            let headers = {
                'Content-Type': 'application/json',
            };

            if (GLOBAL_TOKEN_TYPE === 'BOTH') {
                // Add both Authorization and x-api-key headers
                headers['Authorization'] = GLOBAL_AUTH_TOKEN;
                if (GLOBAL_API_KEY) {
                    headers['x-api-key'] = GLOBAL_API_KEY;
                }
            } else if (GLOBAL_AUTH_TOKEN) {
                // Use the header based on token type
                const headerKey = GLOBAL_TOKEN_TYPE === 'API_KEY' ? 'x-api-key' : 'Authorization';
                headers[headerKey] = GLOBAL_AUTH_TOKEN;
            }

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
                const response = await fetch('{{graphql_endpoint}}', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(graphQLParams),
                });

                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }

                return await response.json();
            } catch (error) {
                console.error('GraphQL request error:', error);
                throw error;
            }
        };

        const explorerPlugin = GraphiQLPluginExplorer.explorerPlugin();

        function initializeGraphiQL() {
            let defaultHeaders = {};
            
            if (GLOBAL_TOKEN_TYPE === 'BOTH') {
                defaultHeaders = {
                    'Authorization': GLOBAL_AUTH_TOKEN
                };
                if (GLOBAL_API_KEY) {
                    defaultHeaders['x-api-key'] = GLOBAL_API_KEY;
                }
            } else if (GLOBAL_AUTH_TOKEN) {
                const headerKey = GLOBAL_TOKEN_TYPE === 'API_KEY' ? 'x-api-key' : 'Authorization';
                defaultHeaders[headerKey] = GLOBAL_AUTH_TOKEN;
            }

            ReactDOM.render(
                React.createElement(GraphiQL, {
                    fetcher: graphQLFetcher,
                    defaultEditorToolsVisibility: true,
                    plugins: [explorerPlugin],
                    defaultHeaders: JSON.stringify(defaultHeaders, null, 2),
                    shouldPersistHeaders: false
                }),
                document.getElementById('graphiql')
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(React.createElement(AuthTokenForm));
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

