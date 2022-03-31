import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

    const getStats = () => {

        fetch(`http://restapi.eastus2.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            }, (error) => {
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
        const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        return () => clearInterval(interval);
    }, [getStats]);

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
                            <th>Employee Resume</th>
                            <th>Job Description</th>
                        </tr>
                        <tr>
                            <td># Number of employees: {stats['num_employees']}</td>
                        </tr>
                        <tr>
                            <td># Popular field: {stats['popular_field']}</td>
                            <td colspan="2">Unpopular field: {stats['unpopular_field']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Company in need of hiring: {stats['desp_employer']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Company least need of hiring: {stats['least_desp_employer']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
