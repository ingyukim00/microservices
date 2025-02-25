// this is processing stats
import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

    useEffect(() => {
        const getStats = () => {
    
            fetch(`http://ec2-18-232-133-253.compute-1.amazonaws.com:8100/stats`)
                .then(res => res.json())
                .then((result) => {
                    console.log("Received Stats")
                    setStats(result); // Sets the state variable 'stats' with the fetched data
                    setIsLoaded(true);
                }, (error) => {
                    setError(error)
                    setIsLoaded(true);
                })
        };
        const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        return () => clearInterval(interval);
    }, []);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false) {
        return (<div>Loading...</div>)
    } else if (isLoaded === true) {
        return (
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
                    <tbody>
                        <tr>
                            <th>Create Recipe Events</th>
                            <th>Rate Recipe Events</th>
                        </tr>
                        <tr>
                            <td>Average Ratings Rating Value</td>
                            <td>{stats['avg_ratings_rating_value']}</td>
                        </tr>
                        <tr>
                            <td>Average Recipe View Value</td>
                            <td>{stats['avg_recipe_view_value']}</td>
                        </tr>
                        <tr>
                            <td>Median Ratings Rating Value</td>
                            <td>{stats['median_ratings_rating_value']}</td>
                        </tr>
                        <tr>
                            <td>Median Recipe View Value</td>
                            <td>{stats['median_recipe_view_value']}</td>
                        </tr>
                        <tr>
                            <td>Number of Ratings</td>
                            <td>{stats['num_ratings']}</td>
                        </tr>
                        <tr>
                            <td>Number of Recipes</td>
                            <td>{stats['num_recipes']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
