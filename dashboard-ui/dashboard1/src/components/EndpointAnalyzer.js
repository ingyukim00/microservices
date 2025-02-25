// this is analyzer stats
import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointAnalyzer(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null)
    const [index, setIndex] = useState(null);
    
	useEffect(() => {
        const getAnalyzer = () => {
            const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
            const url = `http://ec2-18-232-133-253.compute-1.amazonaws.com:8110/${props.endpoint}?index=${rand_val}`;
            console.log("Fetching from URL:", url);
            fetch(url)
            .then(res => {
                if (!res.ok) {
    
                    throw new Error(`API request failed with status ${res.status}`);
                }
                return res.json();
            })
                .then((result)=>{
                    console.log("Received Analyzer Results for " + props.endpoint)
                    setLog(result);
                    setIndex(rand_val);
                    setIsLoaded(true);
                },(error) =>{
                    setError(error)
                    setIsLoaded(true);
                })
        };
		const interval = setInterval(() => getAnalyzer(), 4000); // Update every 4 seconds
		return() => clearInterval(interval);
    }, [props.endpoint]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        
        return (
            <div>
                <h3>{props.endpoint} - {index}</h3>
                {JSON.stringify(log)}
            </div>
        );
    }
}
