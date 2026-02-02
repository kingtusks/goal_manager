import { useState, useEffect } from 'react';

export default function App() {
  const [goals, setGoals] = useState([]);
  useEffect(() => {
    fetch('http://localhost:8000/goals') //get all goals
      .then(res => res.json()) //converts to json
      .then(data => {
        console.log(data); //prints it then
        setGoals(data); //puts the data into goals
      })
      .catch(error => console.error('Error:', error)); //error catching
  }, []);

  return (
    //stringifies goals and yea seems pretty easy
    <div style={{ padding: '20px' }}>
      <h1>My Goals</h1>
      <pre>{JSON.stringify(goals, null, 2)}</pre> 
    </div>
  );
}
