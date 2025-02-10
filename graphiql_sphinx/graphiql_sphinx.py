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
    <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>

    <div id="graphiql" style="height: 80vh; width: 70vw; padding-left: 1vh; margin-top:40px"></div>

    <style>
        /* Existing styles remain unchanged */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            margin: 0 auto;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
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
        button {
            background-color: #2980b9;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #2980b9;
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
            overflow-x: auto;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
    <script type="text/babel">
        const TokenManager = {
            setToken: (token, token_type) => {
                sessionStorage.setItem('graphql_token', token);
                sessionStorage.setItem('token_type', token_type);
                // Dispatch an event to notify token changes
                window.dispatchEvent(new Event('tokenUpdated'));
            },
            getToken: () => {
                return {
                    token: sessionStorage.getItem('graphql_token'),
                    token_type: sessionStorage.getItem('token_type')
                };
            },
            removeToken: () => {
                sessionStorage.removeItem('graphql_token');
                sessionStorage.removeItem('token_type');
                window.dispatchEvent(new Event('tokenUpdated'));
            }
        };

        const AuthTokenForm = () => {
            const [authType, setAuthType] = React.useState('COGNITO');
            const [formData, setFormData] = React.useState({});
            const [response, setResponse] = React.useState(null);
            const [error, setError] = React.useState(null);

            const authFields = {
                COGNITO: ['username', 'password', 'client_id', 'pool_id','region'],
                API_KEY: ['api_key']
            };

            React.useEffect(() => {
                // Check for existing token on component mount
                const existingToken = TokenManager.getToken();
                if (existingToken) {
                    setResponse({ token: existingToken });
                }
            }, []);

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

                    const response = await fetch('http://gerrit.yorkdevs.link:7980/getToken', {
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

                    // Store the token
                    TokenManager.setToken(data.authorization_header, data.token_type);
                    setResponse(data);
                } catch (err) {
                    setError(err.message);
                    TokenManager.removeToken();
                }
            };

            const handleLogout = () => {
                TokenManager.removeToken();
                setResponse(null);
                setFormData({});
            };

            return (
                <div className="container">
                    <h1>Get Authorization Token</h1>
                    {!response ? (
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Authentication Type</label>
                                <select 
                                    value={authType}
                                    onChange={(e) => {
                                        setAuthType(e.target.value);
                                        setFormData({});
                                    }}
                                >
                                    {Object.keys(authFields).map(type => (
                                        <option key={type} value={type}>{type}</option>
                                    ))}
                                </select>
                            </div>

                            {authFields[authType].map(field => (
                                <div key={field} className="form-group">
                                    <label>
                                        {field.split('_').map(word => 
                                            word.charAt(0).toUpperCase() + word.slice(1)
                                        ).join(' ')}
                                    </label>
                                    <input
                                        type={field.includes('password') ? 'password' : 'text'}
                                        name={field}
                                        value={formData[field] || ''}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                            ))}  

                            <button type="submit">Login</button>
                        </form>
                    ) : (
                        <div>
                            <div className="response">
                                <h3>Authentication Status: Active</h3>
                                <p>You can now use the GraphiQL explorer below.</p>
                                <br/>
                                <p>Please click the Re-fetch button to Execute Queries.</p>
                            </div>
                            <button onClick={handleLogout}>
                                Logout
                            </button>
                        </div>
                    )}

                    {error && (
                        <div className="error">
                            {error}
                        </div>
                    )}
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<AuthTokenForm />);

        // Function to get the authentication token from the auth template
        async function getAuthToken() {
            try {
                const token = TokenManager.getToken();
                return token;
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
            const authObj = await getAuthToken();
            const authToken = authObj ? authObj.token : null;
            const authType = authObj ? authObj.token_type : null;
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

