import logo from './logo.png';
import './App.css';

import EndpointAnalyzer from './components/EndpointAnalyzer'
import AppStats from './components/AppStats'
import Anomalies from './components/anomaly';

function App() {

    const endpoints = ["created_recipes", "rated_recipes"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAnalyzer key={endpoint} endpoint={endpoint} />
    })

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="150px" width="400px" />
            <div>
                <AppStats />
                <h1>Analyzer Endpoints</h1>
                {rendered_endpoints}
                <h1>Anomalies</h1>
                <Anomalies anomalyType="Too High" />
                <Anomalies anomalyType="Too Low" />
            </div>
        </div>
    );

}



export default App;
